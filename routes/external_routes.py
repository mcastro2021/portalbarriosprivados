"""
Rutas para integraciones externas - Fase 5
==========================================

APIs para servicios de pagos, comunicación, mapas y clima.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from external_integrations import (
    external_integrations, PaymentProvider, CommunicationMessage,
    LocationData, WeatherData
)
from optional_dependencies import (
    GOOGLEMAPS_AVAILABLE, OPENWEATHERMAP_AVAILABLE, GEOPY_AVAILABLE,
    STRIPE_AVAILABLE, PAYPAL_AVAILABLE, SENDGRID_AVAILABLE, BOTO3_AVAILABLE
)
import time

external_bp = Blueprint('external', __name__, url_prefix='/external')

@external_bp.route('/payments/create', methods=['POST'])
@login_required
def create_payment():
    """Crear pago"""
    try:
        data = request.get_json()
        
        amount = data.get('amount')
        description = data.get('description', 'Pago')
        provider = PaymentProvider(data.get('provider', 'mercadopago'))
        
        if not amount:
            return jsonify({"success": False, "error": "Monto requerido"}), 400
        
        payment_response = external_integrations.create_payment(
            amount=amount,
            description=description,
            provider=provider,
            payer_email=current_user.email,
            payer_name=current_user.username,
            external_reference=f"USER_{current_user.id}_{int(time.time())}"
        )
        
        return jsonify(payment_response)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@external_bp.route('/payments/status/<payment_id>')
@login_required
def get_payment_status(payment_id):
    """Obtener estado de pago"""
    try:
        data = request.get_json()
        provider = PaymentProvider(data.get('provider', 'mercadopago'))
        
        status = external_integrations.payment_gateway.get_payment_status(
            payment_id, provider
        )
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@external_bp.route('/notifications/send', methods=['POST'])
@login_required
def send_notification():
    """Enviar notificación"""
    try:
        data = request.get_json()
        
        to = data.get('to')
        message = data.get('message')
        method = data.get('method', 'email')
        subject = data.get('subject', 'Notificación')
        
        if not to or not message:
            return jsonify({"success": False, "error": "Destinatario y mensaje requeridos"}), 400
        
        result = external_integrations.send_notification(
            to=to,
            message=message,
            method=method,
            subject=subject
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@external_bp.route('/location/geocode', methods=['POST'])
@login_required
def geocode_address():
    """Geocodificar dirección"""
    try:
        if not GOOGLEMAPS_AVAILABLE and not GEOPY_AVAILABLE:
            return jsonify({"success": False, "error": "Servicio de geocodificación no disponible"}), 503
        
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({"success": False, "error": "Dirección requerida"}), 400
        
        location = external_integrations.get_location_info(address=address)
        
        if location:
            return jsonify({
                "success": True,
                "location": {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "address": location.address,
                    "formatted_address": location.formatted_address
                }
            })
        else:
            return jsonify({"success": False, "error": "No se pudo geocodificar la dirección"}), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@external_bp.route('/location/reverse-geocode', methods=['POST'])
@login_required
def reverse_geocode():
    """Geocodificación inversa"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({"success": False, "error": "Latitud y longitud requeridas"}), 400
        
        location = external_integrations.get_location_info(
            latitude=latitude, longitude=longitude
        )
        
        if location:
            return jsonify({
                "success": True,
                "location": {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "address": location.address,
                    "city": location.city,
                    "country": location.country
                }
            })
        else:
            return jsonify({"success": False, "error": "No se pudo obtener la dirección"}), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@external_bp.route('/weather/current', methods=['POST'])
@login_required
def get_current_weather():
    """Obtener clima actual"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({"success": False, "error": "Latitud y longitud requeridas"}), 400
        
        weather = external_integrations.get_weather_info(
            latitude=latitude, longitude=longitude, forecast=False
        )
        
        if weather:
            return jsonify({
                "success": True,
                "weather": {
                    "temperature": weather.temperature,
                    "humidity": weather.humidity,
                    "pressure": weather.pressure,
                    "wind_speed": weather.wind_speed,
                    "wind_direction": weather.wind_direction,
                    "description": weather.description,
                    "icon": weather.icon
                }
            })
        else:
            return jsonify({"success": False, "error": "No se pudo obtener el clima"}), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@external_bp.route('/weather/forecast', methods=['POST'])
@login_required
def get_weather_forecast():
    """Obtener pronóstico del tiempo"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        days = data.get('days', 5)
        
        if not latitude or not longitude:
            return jsonify({"success": False, "error": "Latitud y longitud requeridas"}), 400
        
        forecast = external_integrations.get_weather_info(
            latitude=latitude, longitude=longitude, forecast=True
        )
        
        if forecast:
            forecast_data = []
            for weather in forecast[:days]:
                forecast_data.append({
                    "temperature": weather.temperature,
                    "humidity": weather.humidity,
                    "description": weather.description,
                    "icon": weather.icon
                })
            
            return jsonify({
                "success": True,
                "forecast": forecast_data
            })
        else:
            return jsonify({"success": False, "error": "No se pudo obtener el pronóstico"}), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@external_bp.route('/storage/upload', methods=['POST'])
@login_required
def upload_file():
    """Subir archivo a la nube"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "Archivo requerido"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "Archivo requerido"}), 400
        
        # Guardar archivo temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Subir a la nube
            result = external_integrations.upload_to_cloud(
                file_path=temp_path,
                object_name=f"uploads/{current_user.id}/{file.filename}"
            )
            
            # Limpiar archivo temporal
            os.unlink(temp_path)
            
            return jsonify(result)
            
        except Exception as e:
            # Limpiar archivo temporal en caso de error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@external_bp.route('/storage/download/<object_name>')
@login_required
def download_file(object_name):
    """Descargar archivo de la nube"""
    try:
        import tempfile
        import os
        
        temp_path = tempfile.mktemp()
        
        result = external_integrations.storage_service.download_file(
            object_name=object_name,
            file_path=temp_path
        )
        
        if result["success"]:
            from flask import send_file
            return send_file(temp_path, as_attachment=True)
        else:
            return jsonify(result), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@external_bp.route('/cache/get/<key>')
@login_required
def get_cached_data(key):
    """Obtener datos del caché"""
    try:
        data = external_integrations.get_cached_data(key)
        
        if data is not None:
            return jsonify({"success": True, "data": data})
        else:
            return jsonify({"success": False, "error": "Datos no encontrados"}), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@external_bp.route('/cache/set/<key>', methods=['POST'])
@login_required
def set_cached_data(key):
    """Guardar datos en caché"""
    try:
        data = request.get_json()
        value = data.get('value')
        expiration = data.get('expiration', 3600)
        
        if value is None:
            return jsonify({"success": False, "error": "Valor requerido"}), 400
        
        success = external_integrations.set_cached_data(
            key=key,
            data=value,
            expiration=expiration
        )
        
        return jsonify({"success": success})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def init_external_routes(app):
    """Inicializar rutas de integraciones externas"""
    app.register_blueprint(external_bp)
    print("✅ Rutas de integraciones externas registradas correctamente")
