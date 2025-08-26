"""
FASE 5: INTEGRACIÓN AVANZADA Y API EXTERNAS
===========================================

Sistema de integración con APIs externas y servicios de terceros
para expandir las capacidades del portal de barrios privados.
"""

import requests
import json
import hashlib
import hmac
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from urllib.parse import urlencode
import os
from flask import current_app, request
import mercadopago
from twilio.rest import Client
import googlemaps
import openweathermap
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import stripe
import paypalrestsdk
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import boto3
from botocore.exceptions import ClientError
import redis
import jwt

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Tipos de integración disponibles"""
    PAYMENT = "payment"
    COMMUNICATION = "communication"
    MAPPING = "mapping"
    WEATHER = "weather"
    STORAGE = "storage"
    ANALYTICS = "analytics"
    SECURITY = "security"
    NOTIFICATION = "notification"

class PaymentProvider(Enum):
    """Proveedores de pago soportados"""
    MERCADOPAGO = "mercadopago"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    TRANSFERENCIA = "transferencia"

@dataclass
class PaymentRequest:
    """Solicitud de pago"""
    amount: float
    currency: str = "ARS"
    description: str = ""
    external_reference: str = ""
    payer_email: str = ""
    payer_name: str = ""
    items: List[Dict] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.items is None:
            self.items = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PaymentResponse:
    """Respuesta de pago"""
    success: bool
    payment_id: str = ""
    status: str = ""
    message: str = ""
    redirect_url: str = ""
    qr_code: str = ""
    expires_at: datetime = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class WeatherData:
    """Datos meteorológicos"""
    temperature: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: str
    description: str
    icon: str
    forecast: List[Dict] = None
    
    def __post_init__(self):
        if self.forecast is None:
            self.forecast = []

@dataclass
class LocationData:
    """Datos de ubicación"""
    latitude: float
    longitude: float
    address: str = ""
    city: str = ""
    country: str = ""
    postal_code: str = ""
    formatted_address: str = ""

@dataclass
class CommunicationMessage:
    """Mensaje de comunicación"""
    to: str
    from_: str
    subject: str = ""
    body: str = ""
    template_id: str = ""
    variables: Dict = None
    attachments: List[str] = None
    priority: str = "normal"
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}
        if self.attachments is None:
            self.attachments = []

class PaymentGateway:
    """Gateway de pagos unificado"""
    
    def __init__(self):
        self.mercadopago = None
        self.stripe = None
        self.paypal = None
        self._init_providers()
    
    def _init_providers(self):
        """Inicializar proveedores de pago"""
        try:
            # MercadoPago
            mp_token = os.getenv('MERCADOPAGO_ACCESS_TOKEN')
            if mp_token:
                self.mercadopago = mercadopago.SDK(mp_token)
                logger.info("✅ MercadoPago inicializado")
            
            # Stripe
            stripe_key = os.getenv('STRIPE_SECRET_KEY')
            if stripe_key:
                stripe.api_key = stripe_key
                self.stripe = stripe
                logger.info("✅ Stripe inicializado")
            
            # PayPal
            paypal_config = {
                'mode': os.getenv('PAYPAL_MODE', 'sandbox'),
                'client_id': os.getenv('PAYPAL_CLIENT_ID'),
                'client_secret': os.getenv('PAYPAL_CLIENT_SECRET')
            }
            if paypal_config['client_id'] and paypal_config['client_secret']:
                paypalrestsdk.configure(paypal_config)
                self.paypal = paypalrestsdk
                logger.info("✅ PayPal inicializado")
                
        except Exception as e:
            logger.error(f"❌ Error inicializando proveedores de pago: {e}")
    
    def create_payment(self, payment_request: PaymentRequest, provider: PaymentProvider) -> PaymentResponse:
        """Crear pago con el proveedor especificado"""
        try:
            if provider == PaymentProvider.MERCADOPAGO and self.mercadopago:
                return self._create_mercadopago_payment(payment_request)
            elif provider == PaymentProvider.STRIPE and self.stripe:
                return self._create_stripe_payment(payment_request)
            elif provider == PaymentProvider.PAYPAL and self.paypal:
                return self._create_paypal_payment(payment_request)
            else:
                return PaymentResponse(
                    success=False,
                    message=f"Proveedor {provider.value} no disponible"
                )
        except Exception as e:
            logger.error(f"❌ Error creando pago: {e}")
            return PaymentResponse(
                success=False,
                message=f"Error interno: {str(e)}"
            )
    
    def _create_mercadopago_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """Crear pago con MercadoPago"""
        try:
            preference_data = {
                "items": [
                    {
                        "title": payment_request.description,
                        "quantity": 1,
                        "unit_price": float(payment_request.amount)
                    }
                ],
                "external_reference": payment_request.external_reference,
                "payer": {
                    "email": payment_request.payer_email,
                    "name": payment_request.payer_name
                },
                "back_urls": {
                    "success": f"{request.host_url}payment/success",
                    "failure": f"{request.host_url}payment/failure",
                    "pending": f"{request.host_url}payment/pending"
                },
                "auto_return": "approved",
                "notification_url": f"{request.host_url}webhook/mercadopago"
            }
            
            preference_response = self.mercadopago.preference().create(preference_data)
            
            if preference_response["status"] == 201:
                preference = preference_response["response"]
                return PaymentResponse(
                    success=True,
                    payment_id=preference["id"],
                    status="pending",
                    redirect_url=preference["init_point"],
                    qr_code=preference.get("qr_code", ""),
                    expires_at=datetime.now() + timedelta(hours=24),
                    metadata={"preference_id": preference["id"]}
                )
            else:
                return PaymentResponse(
                    success=False,
                    message=f"Error MercadoPago: {preference_response.get('message', 'Unknown error')}"
                )
                
        except Exception as e:
            logger.error(f"❌ Error MercadoPago: {e}")
            return PaymentResponse(
                success=False,
                message=f"Error MercadoPago: {str(e)}"
            )
    
    def _create_stripe_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """Crear pago con Stripe"""
        try:
            # Convertir a centavos para Stripe
            amount_cents = int(payment_request.amount * 100)
            
            payment_intent = self.stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=payment_request.currency.lower(),
                description=payment_request.description,
                metadata=payment_request.metadata
            )
            
            return PaymentResponse(
                success=True,
                payment_id=payment_intent.id,
                status=payment_intent.status,
                redirect_url=f"{request.host_url}payment/stripe/{payment_intent.id}",
                expires_at=datetime.now() + timedelta(hours=24),
                metadata={"client_secret": payment_intent.client_secret}
            )
            
        except Exception as e:
            logger.error(f"❌ Error Stripe: {e}")
            return PaymentResponse(
                success=False,
                message=f"Error Stripe: {str(e)}"
            )
    
    def _create_paypal_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """Crear pago con PayPal"""
        try:
            payment = self.paypal.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": f"{request.host_url}payment/paypal/success",
                    "cancel_url": f"{request.host_url}payment/paypal/cancel"
                },
                "transactions": [{
                    "item_list": {
                        "items": [
                            {
                                "name": payment_request.description,
                                "sku": payment_request.external_reference,
                                "price": str(payment_request.amount),
                                "currency": payment_request.currency,
                                "quantity": 1
                            }
                        ]
                    },
                    "amount": {
                        "total": str(payment_request.amount),
                        "currency": payment_request.currency
                    },
                    "description": payment_request.description
                }]
            })
            
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
                return PaymentResponse(
                    success=True,
                    payment_id=payment.id,
                    status="pending",
                    redirect_url=approval_url,
                    expires_at=datetime.now() + timedelta(hours=24),
                    metadata={"payment_id": payment.id}
                )
            else:
                return PaymentResponse(
                    success=False,
                    message=f"Error PayPal: {payment.error}"
                )
                
        except Exception as e:
            logger.error(f"❌ Error PayPal: {e}")
            return PaymentResponse(
                success=False,
                message=f"Error PayPal: {str(e)}"
            )
    
    def get_payment_status(self, payment_id: str, provider: PaymentProvider) -> Dict:
        """Obtener estado de un pago"""
        try:
            if provider == PaymentProvider.MERCADOPAGO and self.mercadopago:
                payment_info = self.mercadopago.payment().get(payment_id)
                if payment_info["status"] == 200:
                    return {
                        "status": payment_info["response"]["status"],
                        "amount": payment_info["response"]["transaction_amount"],
                        "currency": payment_info["response"]["currency_id"],
                        "payment_method": payment_info["response"]["payment_method"]["type"],
                        "created_at": payment_info["response"]["date_created"]
                    }
            
            elif provider == PaymentProvider.STRIPE and self.stripe:
                payment_intent = self.stripe.PaymentIntent.retrieve(payment_id)
                return {
                    "status": payment_intent.status,
                    "amount": payment_intent.amount / 100,
                    "currency": payment_intent.currency,
                    "payment_method": payment_intent.payment_method_types[0] if payment_intent.payment_method_types else None,
                    "created_at": datetime.fromtimestamp(payment_intent.created)
                }
            
            return {"error": "Proveedor no disponible"}
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado de pago: {e}")
            return {"error": str(e)}

class CommunicationService:
    """Servicio de comunicación unificado"""
    
    def __init__(self):
        self.twilio = None
        self.sendgrid = None
        self._init_providers()
    
    def _init_providers(self):
        """Inicializar proveedores de comunicación"""
        try:
            # Twilio
            twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            if twilio_account_sid and twilio_auth_token:
                self.twilio = Client(twilio_account_sid, twilio_auth_token)
                logger.info("✅ Twilio inicializado")
            
            # SendGrid
            sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
            if sendgrid_api_key:
                self.sendgrid = SendGridAPIClient(api_key=sendgrid_api_key)
                logger.info("✅ SendGrid inicializado")
                
        except Exception as e:
            logger.error(f"❌ Error inicializando proveedores de comunicación: {e}")
    
    def send_sms(self, to: str, message: str, from_: str = None) -> Dict:
        """Enviar SMS"""
        try:
            if not self.twilio:
                return {"success": False, "error": "Twilio no configurado"}
            
            from_number = from_ or os.getenv('TWILIO_PHONE_NUMBER')
            if not from_number:
                return {"success": False, "error": "Número de origen no configurado"}
            
            message_obj = self.twilio.messages.create(
                body=message,
                from_=from_number,
                to=to
            )
            
            return {
                "success": True,
                "message_id": message_obj.sid,
                "status": message_obj.status
            }
            
        except Exception as e:
            logger.error(f"❌ Error enviando SMS: {e}")
            return {"success": False, "error": str(e)}
    
    def send_email(self, message: CommunicationMessage) -> Dict:
        """Enviar email"""
        try:
            if not self.sendgrid:
                return {"success": False, "error": "SendGrid no configurado"}
            
            mail = Mail(
                from_email=message.from_,
                to_emails=message.to,
                subject=message.subject,
                html_content=message.body
            )
            
            if message.template_id:
                mail.template_id = message.template_id
                mail.dynamic_template_data = message.variables
            
            response = self.sendgrid.send(mail)
            
            return {
                "success": response.status_code == 202,
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }
            
        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}")
            return {"success": False, "error": str(e)}
    
    def send_whatsapp(self, to: str, message: str, media_url: str = None) -> Dict:
        """Enviar WhatsApp (usando Twilio)"""
        try:
            if not self.twilio:
                return {"success": False, "error": "Twilio no configurado"}
            
            from_number = f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER', '')}"
            to_number = f"whatsapp:{to}"
            
            message_data = {
                "body": message,
                "from_": from_number,
                "to": to_number
            }
            
            if media_url:
                message_data["media_url"] = [media_url]
            
            message_obj = self.twilio.messages.create(**message_data)
            
            return {
                "success": True,
                "message_id": message_obj.sid,
                "status": message_obj.status
            }
            
        except Exception as e:
            logger.error(f"❌ Error enviando WhatsApp: {e}")
            return {"success": False, "error": str(e)}

class MappingService:
    """Servicio de mapas y geolocalización"""
    
    def __init__(self):
        self.gmaps = None
        self.geolocator = None
        self._init_providers()
    
    def _init_providers(self):
        """Inicializar proveedores de mapas"""
        try:
            # Google Maps
            google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            if google_api_key:
                self.gmaps = googlemaps.Client(key=google_api_key)
                logger.info("✅ Google Maps inicializado")
            
            # Geopy (Nominatim)
            self.geolocator = Nominatim(user_agent="portalbarriosprivados")
            logger.info("✅ Geopy inicializado")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando proveedores de mapas: {e}")
    
    def geocode_address(self, address: str) -> Optional[LocationData]:
        """Geocodificar dirección"""
        try:
            if self.gmaps:
                # Usar Google Maps
                result = self.gmaps.geocode(address)
                if result:
                    location = result[0]['geometry']['location']
                    return LocationData(
                        latitude=location['lat'],
                        longitude=location['lng'],
                        address=address,
                        formatted_address=result[0]['formatted_address']
                    )
            
            elif self.geolocator:
                # Usar Nominatim como fallback
                location = self.geolocator.geocode(address)
                if location:
                    return LocationData(
                        latitude=location.latitude,
                        longitude=location.longitude,
                        address=address,
                        formatted_address=location.address
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error geocodificando dirección: {e}")
            return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[LocationData]:
        """Geocodificación inversa"""
        try:
            if self.gmaps:
                # Usar Google Maps
                result = self.gmaps.reverse_geocode((latitude, longitude))
                if result:
                    address_components = result[0]['address_components']
                    return LocationData(
                        latitude=latitude,
                        longitude=longitude,
                        address=result[0]['formatted_address'],
                        city=self._extract_component(address_components, 'locality'),
                        country=self._extract_component(address_components, 'country'),
                        postal_code=self._extract_component(address_components, 'postal_code')
                    )
            
            elif self.geolocator:
                # Usar Nominatim como fallback
                location = self.geolocator.reverse(f"{latitude}, {longitude}")
                if location:
                    return LocationData(
                        latitude=latitude,
                        longitude=longitude,
                        address=location.address
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error en geocodificación inversa: {e}")
            return None
    
    def _extract_component(self, components: List[Dict], type_: str) -> str:
        """Extraer componente de dirección"""
        for component in components:
            if type_ in component['types']:
                return component['long_name']
        return ""
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcular distancia entre dos puntos"""
        try:
            point1 = (lat1, lon1)
            point2 = (lat2, lon2)
            return geodesic(point1, point2).kilometers
        except Exception as e:
            logger.error(f"❌ Error calculando distancia: {e}")
            return 0.0
    
    def get_nearby_places(self, latitude: float, longitude: float, radius: int = 5000, type_: str = None) -> List[Dict]:
        """Obtener lugares cercanos"""
        try:
            if not self.gmaps:
                return []
            
            places_result = self.gmaps.places_nearby(
                location=(latitude, longitude),
                radius=radius,
                type=type_
            )
            
            return places_result.get('results', [])
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo lugares cercanos: {e}")
            return []

class WeatherService:
    """Servicio meteorológico"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, latitude: float, longitude: float, units: str = "metric") -> Optional[WeatherData]:
        """Obtener clima actual"""
        try:
            if not self.api_key:
                logger.warning("⚠️ API key de OpenWeather no configurada")
                return None
            
            url = f"{self.base_url}/weather"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": units,
                "lang": "es"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return WeatherData(
                temperature=data['main']['temp'],
                humidity=data['main']['humidity'],
                pressure=data['main']['pressure'],
                wind_speed=data['wind']['speed'],
                wind_direction=self._get_wind_direction(data['wind']['deg']),
                description=data['weather'][0]['description'],
                icon=data['weather'][0]['icon']
            )
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo clima actual: {e}")
            return None
    
    def get_forecast(self, latitude: float, longitude: float, days: int = 5, units: str = "metric") -> List[WeatherData]:
        """Obtener pronóstico del tiempo"""
        try:
            if not self.api_key:
                return []
            
            url = f"{self.base_url}/forecast"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": units,
                "lang": "es"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            forecast = []
            
            for item in data['list'][:days * 8]:  # 8 mediciones por día
                weather = WeatherData(
                    temperature=item['main']['temp'],
                    humidity=item['main']['humidity'],
                    pressure=item['main']['pressure'],
                    wind_speed=item['wind']['speed'],
                    wind_direction=self._get_wind_direction(item['wind']['deg']),
                    description=item['weather'][0]['description'],
                    icon=item['weather'][0]['icon']
                )
                forecast.append(weather)
            
            return forecast
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pronóstico: {e}")
            return []
    
    def _get_wind_direction(self, degrees: float) -> str:
        """Convertir grados a dirección del viento"""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]

class StorageService:
    """Servicio de almacenamiento en la nube"""
    
    def __init__(self):
        self.s3 = None
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        self._init_s3()
    
    def _init_s3(self):
        """Inicializar AWS S3"""
        try:
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            
            if aws_access_key and aws_secret_key:
                self.s3 = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )
                logger.info("✅ AWS S3 inicializado")
                
        except Exception as e:
            logger.error(f"❌ Error inicializando S3: {e}")
    
    def upload_file(self, file_path: str, object_name: str = None) -> Dict:
        """Subir archivo a S3"""
        try:
            if not self.s3 or not self.bucket_name:
                return {"success": False, "error": "S3 no configurado"}
            
            if object_name is None:
                object_name = os.path.basename(file_path)
            
            self.s3.upload_file(file_path, self.bucket_name, object_name)
            
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{object_name}"
            
            return {
                "success": True,
                "url": url,
                "object_name": object_name
            }
            
        except Exception as e:
            logger.error(f"❌ Error subiendo archivo: {e}")
            return {"success": False, "error": str(e)}
    
    def upload_fileobj(self, file_obj, object_name: str, content_type: str = None) -> Dict:
        """Subir objeto de archivo a S3"""
        try:
            if not self.s3 or not self.bucket_name:
                return {"success": False, "error": "S3 no configurado"}
            
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3.upload_fileobj(file_obj, self.bucket_name, object_name, ExtraArgs=extra_args)
            
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{object_name}"
            
            return {
                "success": True,
                "url": url,
                "object_name": object_name
            }
            
        except Exception as e:
            logger.error(f"❌ Error subiendo objeto: {e}")
            return {"success": False, "error": str(e)}
    
    def download_file(self, object_name: str, file_path: str) -> Dict:
        """Descargar archivo de S3"""
        try:
            if not self.s3 or not self.bucket_name:
                return {"success": False, "error": "S3 no configurado"}
            
            self.s3.download_file(self.bucket_name, object_name, file_path)
            
            return {
                "success": True,
                "file_path": file_path
            }
            
        except Exception as e:
            logger.error(f"❌ Error descargando archivo: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_file(self, object_name: str) -> Dict:
        """Eliminar archivo de S3"""
        try:
            if not self.s3 or not self.bucket_name:
                return {"success": False, "error": "S3 no configurado"}
            
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"❌ Error eliminando archivo: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> Dict:
        """Generar URL firmada temporal"""
        try:
            if not self.s3 or not self.bucket_name:
                return {"success": False, "error": "S3 no configurado"}
            
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            
            return {
                "success": True,
                "url": url,
                "expires_in": expiration
            }
            
        except Exception as e:
            logger.error(f"❌ Error generando URL firmada: {e}")
            return {"success": False, "error": str(e)}

class ExternalIntegrationsManager:
    """Gestor principal de integraciones externas"""
    
    def __init__(self):
        self.payment_gateway = PaymentGateway()
        self.communication_service = CommunicationService()
        self.mapping_service = MappingService()
        self.weather_service = WeatherService()
        self.storage_service = StorageService()
        self.redis_client = None
        self._init_cache()
    
    def _init_cache(self):
        """Inicializar caché Redis"""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info("✅ Redis cache inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible: {e}")
    
    def create_payment(self, amount: float, description: str, provider: PaymentProvider, **kwargs) -> PaymentResponse:
        """Crear pago"""
        payment_request = PaymentRequest(
            amount=amount,
            description=description,
            **kwargs
        )
        return self.payment_gateway.create_payment(payment_request, provider)
    
    def send_notification(self, to: str, message: str, method: str = "email", **kwargs) -> Dict:
        """Enviar notificación"""
        if method == "sms":
            return self.communication_service.send_sms(to, message, **kwargs)
        elif method == "whatsapp":
            return self.communication_service.send_whatsapp(to, message, **kwargs)
        else:
            comm_message = CommunicationMessage(
                to=to,
                from_=kwargs.get('from_', os.getenv('DEFAULT_FROM_EMAIL')),
                subject=kwargs.get('subject', 'Notificación'),
                body=message
            )
            return self.communication_service.send_email(comm_message)
    
    def get_location_info(self, address: str = None, latitude: float = None, longitude: float = None) -> Optional[LocationData]:
        """Obtener información de ubicación"""
        if address:
            return self.mapping_service.geocode_address(address)
        elif latitude and longitude:
            return self.mapping_service.reverse_geocode(latitude, longitude)
        return None
    
    def get_weather_info(self, latitude: float, longitude: float, forecast: bool = False) -> Union[WeatherData, List[WeatherData]]:
        """Obtener información meteorológica"""
        if forecast:
            return self.weather_service.get_forecast(latitude, longitude)
        else:
            return self.weather_service.get_current_weather(latitude, longitude)
    
    def upload_to_cloud(self, file_path: str, object_name: str = None) -> Dict:
        """Subir archivo a la nube"""
        return self.storage_service.upload_file(file_path, object_name)
    
    def get_cached_data(self, key: str) -> Any:
        """Obtener datos del caché"""
        if not self.redis_client:
            return None
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"❌ Error obteniendo caché: {e}")
            return None
    
    def set_cached_data(self, key: str, data: Any, expiration: int = 3600) -> bool:
        """Guardar datos en caché"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.setex(key, expiration, json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"❌ Error guardando caché: {e}")
            return False

# Instancia global
external_integrations = ExternalIntegrationsManager()

def init_external_integrations(app):
    """Inicializar integraciones externas en la aplicación Flask"""
    try:
        # Registrar en el contexto de la aplicación
        app.external_integrations = external_integrations
        
        # Configurar webhooks
        @app.route('/webhook/mercadopago', methods=['POST'])
        def mercadopago_webhook():
            """Webhook de MercadoPago"""
            try:
                data = request.get_json()
                payment_id = data.get('data', {}).get('id')
                
                if payment_id:
                    # Procesar notificación de pago
                    status = external_integrations.payment_gateway.get_payment_status(
                        payment_id, PaymentProvider.MERCADOPAGO
                    )
                    
                    # Aquí puedes agregar lógica para actualizar el estado en tu base de datos
                    logger.info(f"Webhook MercadoPago: Pago {payment_id} - Estado: {status}")
                
                return jsonify({"status": "ok"}), 200
                
            except Exception as e:
                logger.error(f"❌ Error en webhook MercadoPago: {e}")
                return jsonify({"error": str(e)}), 500
        
        @app.route('/webhook/stripe', methods=['POST'])
        def stripe_webhook():
            """Webhook de Stripe"""
            try:
                payload = request.get_data()
                sig_header = request.headers.get('Stripe-Signature')
                
                # Verificar firma (requiere endpoint_secret)
                endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
                if endpoint_secret:
                    event = stripe.Webhook.construct_event(
                        payload, sig_header, endpoint_secret
                    )
                else:
                    event = json.loads(payload)
                
                # Procesar evento
                if event['type'] == 'payment_intent.succeeded':
                    payment_intent = event['data']['object']
                    logger.info(f"Webhook Stripe: Pago {payment_intent['id']} completado")
                
                return jsonify({"status": "ok"}), 200
                
            except Exception as e:
                logger.error(f"❌ Error en webhook Stripe: {e}")
                return jsonify({"error": str(e)}), 500
        
        logger.info("✅ Integraciones externas inicializadas correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando integraciones externas: {e}")

if __name__ == "__main__":
    # Ejemplo de uso
    print("🚀 Sistema de Integraciones Externas - Fase 5")
    print("=" * 50)
    
    # Crear instancia
    integrations = ExternalIntegrationsManager()
    
    # Ejemplo de pago
    payment_response = integrations.create_payment(
        amount=1000.0,
        description="Pago de cuota mensual",
        provider=PaymentProvider.MERCADOPAGO,
        payer_email="usuario@ejemplo.com",
        external_reference="CUOTA_001"
    )
    
    print(f"Pago creado: {payment_response.success}")
    if payment_response.success:
        print(f"ID: {payment_response.payment_id}")
        print(f"URL: {payment_response.redirect_url}")
    
    print("\n✅ Fase 5: Integración Avanzada y APIs Externas completada")
