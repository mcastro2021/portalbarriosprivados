"""
Base de conocimiento del barrio para el chatbot inteligente
Contiene reglamentos, horarios, contactos y procedimientos
"""

from datetime import datetime, timedelta
import re

class BarrioKnowledgeBase:
    """Base de conocimiento específica del barrio"""
    
    def __init__(self):
        self.reglamentos = {
            'pileta': {
                'titulo': 'Construcción de Piletas',
                'contenido': """
                Para construir una pileta debes:
                1. Solicitar autorización al consorcio con planos
                2. Cumplir distancias mínimas: 3m del fondo, 2m laterales
                3. Sistema de filtrado silencioso
                4. Cerco perimetral obligatorio (min 1.2m altura)
                5. Horario de construcción: 8:00-18:00 días hábiles
                6. Seguro de responsabilidad civil vigente
                """,
                'contacto': 'administracion@barrio.com',
                'tiempo_aprobacion': '15-30 días hábiles'
            },
            'construccion': {
                'titulo': 'Obras y Construcciones',
                'contenido': """
                Reglamento general de construcciones:
                1. Autorización previa obligatoria
                2. Horarios: Lunes a Viernes 8:00-18:00, Sábados 9:00-13:00
                3. No se permite trabajo domingos y feriados
                4. Altura máxima: 2 pisos + mansarda
                5. Retiros: Frente 5m, laterales 3m, fondo 3m
                6. Factor de ocupación máximo: 60%
                """,
                'multa_incumplimiento': '$50,000 por día'
            },
            'mascotas': {
                'titulo': 'Reglamento de Mascotas',
                'contenido': """
                1. Máximo 2 mascotas por lote
                2. Siempre con correa en espacios comunes
                3. Recoger excrementos obligatorio
                4. Horario de paseo en quincho: 7:00-9:00 y 19:00-21:00
                5. Vacunas al día (presentar certificado anual)
                6. Prohibido ladridos excesivos (22:00-8:00)
                """,
                'multa': '$15,000 por infracción'
            },
            'ruidos': {
                'titulo': 'Reglamento de Ruidos',
                'contenido': """
                Horarios de silencio:
                - Lunes a Jueves: 22:00 - 8:00
                - Viernes y Sábados: 24:00 - 8:00
                - Domingos: 22:00 - 10:00
                
                Prohibido:
                - Música alta fuera de horarios
                - Herramientas ruidosas en horarios de silencio
                - Fiestas sin autorización previa
                """,
                'excepcion': 'Fiestas autorizadas hasta 2:00 AM máximo 2 veces/año'
            }
        }
        
        self.horarios = {
            'administracion': {
                'horario': 'Lunes a Viernes 9:00-17:00',
                'telefono': '+54 11 4444-5555',
                'email': 'administracion@barrio.com',
                'whatsapp': '+54 9 11 4444-5555'
            },
            'seguridad': {
                'horario': '24/7 todos los días',
                'telefono': '+54 11 4444-5556',
                'emergencias': '911 o +54 11 4444-5556'
            },
            'mantenimiento': {
                'horario': 'Lunes a Viernes 8:00-16:00',
                'telefono': '+54 11 4444-5557',
                'email': 'mantenimiento@barrio.com'
            },
            'quincho': {
                'horario_reservas': 'Lunes a Domingos 10:00-22:00',
                'horario_uso': 'Hasta 24:00 (Viernes/Sábado hasta 2:00)',
                'capacidad': '80 personas máximo',
                'precio': '$25,000/día'
            },
            'cancha_tenis': {
                'horario': '8:00-22:00 todos los días',
                'reserva_maxima': '2 horas consecutivas',
                'precio': '$5,000/hora',
                'iluminacion': 'Incluida hasta 22:00'
            },
            'pileta_comunitaria': {
                'temporada': 'Octubre - Abril',
                'horario': '10:00-20:00',
                'capacidad': '50 personas',
                'guardavidas': 'Obligatorio - incluido'
            }
        }
        
        self.contactos = {
            'emergencias': {
                'policia': '911',
                'bomberos': '100',
                'ambulancia': '107',
                'seguridad_barrio': '+54 11 4444-5556'
            },
            'servicios': {
                'administracion': '+54 11 4444-5555',
                'mantenimiento': '+54 11 4444-5557',
                'limpieza': '+54 11 4444-5558',
                'jardineria': '+54 11 4444-5559'
            },
            'consorcio': {
                'presidente': 'Carlos Mendez - carlos.mendez@email.com',
                'secretario': 'Ana Rodriguez - ana.rodriguez@email.com',
                'tesorero': 'Luis García - luis.garcia@email.com'
            }
        }
        
        self.procedimientos = {
            'mudanza': {
                'aviso_previo': '48 horas',
                'horario': 'Lunes a Sábado 8:00-18:00',
                'deposito': '$50,000 (reintegrable)',
                'contacto': 'administracion@barrio.com'
            },
            'obras_menores': {
                'definicion': 'Pintura, pisos, instalaciones internas',
                'autorizacion': 'No requerida',
                'horario': 'Lunes a Viernes 8:00-17:00, Sábados 9:00-13:00'
            },
            'obras_mayores': {
                'definicion': 'Ampliaciones, piletas, modificaciones estructurales',
                'autorizacion': 'Obligatoria - planos y memoria técnica',
                'tiempo_aprobacion': '15-30 días',
                'seguro': 'RC obligatorio mínimo $10.000.000'
            }
        }

    def buscar_respuesta(self, consulta):
        """Busca respuesta en la base de conocimiento"""
        consulta_lower = consulta.lower()
        
        # Buscar en reglamentos
        for key, reglamento in self.reglamentos.items():
            if any(palabra in consulta_lower for palabra in self._get_keywords(key)):
                return self._format_reglamento_response(reglamento)
        
        # Buscar horarios
        if any(palabra in consulta_lower for palabra in ['horario', 'hora', 'cuando', 'abre', 'cierra']):
            return self._buscar_horarios(consulta_lower)
        
        # Buscar contactos
        if any(palabra in consulta_lower for palabra in ['telefono', 'contacto', 'numero', 'llamar', 'whatsapp']):
            return self._buscar_contactos(consulta_lower)
        
        # Buscar procedimientos
        if any(palabra in consulta_lower for palabra in ['como', 'proceso', 'tramite', 'procedimiento']):
            return self._buscar_procedimientos(consulta_lower)
        
        return None

    def _get_keywords(self, tipo):
        """Obtiene palabras clave para cada tipo de consulta"""
        keywords = {
            'pileta': ['pileta', 'piscina', 'construir pileta', 'swimming pool'],
            'construccion': ['construccion', 'obra', 'construir', 'ampliacion', 'edificar'],
            'mascotas': ['mascota', 'perro', 'gato', 'animal', 'pet'],
            'ruidos': ['ruido', 'musica', 'silencio', 'molestia', 'fiesta']
        }
        return keywords.get(tipo, [])

    def _format_reglamento_response(self, reglamento):
        """Formatea respuesta de reglamento"""
        response = f"📋 **{reglamento['titulo']}**\n\n{reglamento['contenido']}"
        
        if 'contacto' in reglamento:
            response += f"\n📞 **Contacto**: {reglamento['contacto']}"
        if 'tiempo_aprobacion' in reglamento:
            response += f"\n⏱️ **Tiempo de aprobación**: {reglamento['tiempo_aprobacion']}"
        if 'multa' in reglamento:
            response += f"\n⚠️ **Multa por incumplimiento**: {reglamento['multa']}"
        
        return response

    def _buscar_horarios(self, consulta):
        """Busca información de horarios"""
        if 'administracion' in consulta:
            info = self.horarios['administracion']
            return f"🏢 **Administración**\n📅 {info['horario']}\n📞 {info['telefono']}\n📧 {info['email']}\n📱 WhatsApp: {info['whatsapp']}"
        
        elif 'seguridad' in consulta:
            info = self.horarios['seguridad']
            return f"🛡️ **Seguridad**\n📅 {info['horario']}\n📞 {info['telefono']}\n🚨 Emergencias: {info['emergencias']}"
        
        elif any(palabra in consulta for palabra in ['quincho', 'salon']):
            info = self.horarios['quincho']
            return f"🏛️ **Quincho/Salón de Fiestas**\n📅 Reservas: {info['horario_reservas']}\n🕐 Uso: {info['horario_uso']}\n👥 Capacidad: {info['capacidad']}\n💰 Precio: {info['precio']}"
        
        elif any(palabra in consulta for palabra in ['tenis', 'cancha']):
            info = self.horarios['cancha_tenis']
            return f"🎾 **Cancha de Tenis**\n📅 {info['horario']}\n⏰ Reserva máxima: {info['reserva_maxima']}\n💰 {info['precio']}\n💡 {info['iluminacion']}"
        
        elif 'pileta' in consulta:
            info = self.horarios['pileta_comunitaria']
            return f"🏊 **Pileta Comunitaria**\n📅 Temporada: {info['temporada']}\n🕐 Horario: {info['horario']}\n👥 Capacidad: {info['capacidad']}\n🏊‍♂️ {info['guardavidas']}"
        
        return "🕐 **Horarios Generales:**\n• Administración: Lun-Vie 9:00-17:00\n• Seguridad: 24/7\n• Mantenimiento: Lun-Vie 8:00-16:00\n• Quincho: 10:00-22:00 (uso hasta 24:00)\n• Cancha Tenis: 8:00-22:00"

    def _buscar_contactos(self, consulta):
        """Busca información de contactos"""
        if 'emergencia' in consulta:
            return "🚨 **Contactos de Emergencia:**\n• Policía: 911\n• Bomberos: 100\n• Ambulancia: 107\n• Seguridad Barrio: +54 11 4444-5556"
        
        elif 'administracion' in consulta:
            return "🏢 **Administración:**\n• Teléfono: +54 11 4444-5555\n• Email: administracion@barrio.com\n• WhatsApp: +54 9 11 4444-5555"
        
        elif 'consorcio' in consulta:
            return "🏛️ **Consorcio:**\n• Presidente: Carlos Mendez - carlos.mendez@email.com\n• Secretario: Ana Rodriguez - ana.rodriguez@email.com\n• Tesorero: Luis García - luis.garcia@email.com"
        
        return "📞 **Contactos Principales:**\n• Administración: +54 11 4444-5555\n• Seguridad: +54 11 4444-5556\n• Mantenimiento: +54 11 4444-5557\n• Emergencias: 911"

    def _buscar_procedimientos(self, consulta):
        """Busca información de procedimientos"""
        if 'mudanza' in consulta:
            proc = self.procedimientos['mudanza']
            return f"📦 **Procedimiento de Mudanza:**\n• Aviso previo: {proc['aviso_previo']}\n• Horario permitido: {proc['horario']}\n• Depósito: {proc['deposito']}\n• Contacto: {proc['contacto']}"
        
        elif any(palabra in consulta for palabra in ['obra menor', 'pintura', 'piso']):
            proc = self.procedimientos['obras_menores']
            return f"🔨 **Obras Menores ({proc['definicion']}):**\n• Autorización: {proc['autorizacion']}\n• Horario: {proc['horario']}"
        
        elif any(palabra in consulta for palabra in ['obra mayor', 'ampliacion', 'pileta']):
            proc = self.procedimientos['obras_mayores']
            return f"🏗️ **Obras Mayores ({proc['definicion']}):**\n• Autorización: {proc['autorizacion']}\n• Tiempo: {proc['tiempo_aprobacion']}\n• Seguro: {proc['seguro']}"
        
        return None

class BarrioDataAnalyzer:
    """Analizador de datos del barrio en tiempo real"""
    
    def __init__(self, db):
        self.db = db
    
    def get_expense_info(self, user_id):
        """Obtiene información de expensas del usuario"""
        from models import Expense
        
        # Expensas pendientes
        pending = Expense.query.filter_by(user_id=user_id, status='pending').all()
        overdue = Expense.query.filter_by(user_id=user_id, status='overdue').all()
        
        if not pending and not overdue:
            return "✅ **Estado de Expensas:** ¡Excelente! No tienes expensas pendientes."
        
        response = "💳 **Estado de tus Expensas:**\n\n"
        
        if pending:
            response += f"📋 **Pendientes ({len(pending)}):**\n"
            for exp in pending:
                response += f"• Período: {exp.period}\n• Monto: ${exp.amount:,.0f}\n• Vence: {exp.due_date.strftime('%d/%m/%Y')}\n\n"
        
        if overdue:
            response += f"⚠️ **Vencidas ({len(overdue)}):**\n"
            for exp in overdue:
                days_overdue = (datetime.now().date() - exp.due_date).days
                response += f"• Período: {exp.period}\n• Monto: ${exp.amount:,.0f}\n• Vencida hace: {days_overdue} días\n\n"
        
        return response.strip()
    
    def get_visits_info(self, user_id):
        """Obtiene información de visitas del usuario"""
        from models import Visit
        
        pending = Visit.query.filter_by(resident_id=user_id, status='pending').all()
        active = Visit.query.filter_by(resident_id=user_id, status='active').all()
        
        if not pending and not active:
            return "👥 **Visitas:** No tienes visitas pendientes ni activas en este momento."
        
        response = "👥 **Estado de tus Visitas:**\n\n"
        
        if pending:
            response += f"⏳ **Pendientes de autorización ({len(pending)}):**\n"
            for visit in pending[:3]:  # Máximo 3
                response += f"• {visit.visitor_name} - {visit.visit_date.strftime('%d/%m/%Y')}\n"
            if len(pending) > 3:
                response += f"• ... y {len(pending) - 3} más\n"
            response += "\n"
        
        if active:
            response += f"✅ **Autorizadas ({len(active)}):**\n"
            for visit in active[:3]:
                response += f"• {visit.visitor_name} - {visit.visit_date.strftime('%d/%m/%Y')}\n"
            if len(active) > 3:
                response += f"• ... y {len(active) - 3} más\n"
        
        return response.strip()
    
    def get_reservations_info(self, user_id):
        """Obtiene información de reservas del usuario"""
        from models import Reservation
        
        pending = Reservation.query.filter_by(user_id=user_id, status='pending').all()
        approved = Reservation.query.filter_by(user_id=user_id, status='approved').all()
        
        if not pending and not approved:
            return "📅 **Reservas:** No tienes reservas pendientes ni confirmadas."
        
        response = "📅 **Estado de tus Reservas:**\n\n"
        
        if pending:
            response += f"⏳ **Pendientes de aprobación ({len(pending)}):**\n"
            for res in pending:
                response += f"• {res.space_type} - {res.date.strftime('%d/%m/%Y')}\n"
            response += "\n"
        
        if approved:
            response += f"✅ **Confirmadas ({len(approved)}):**\n"
            for res in approved:
                response += f"• {res.space_type} - {res.date.strftime('%d/%m/%Y')}\n"
        
        return response.strip()

class AIClaimClassifier:
    """Clasificador automático de reclamos con IA"""
    
    def __init__(self):
        self.categorias = {
            'seguridad': {
                'keywords': ['robo', 'seguridad', 'alarma', 'intruso', 'guardia', 'camara', 'iluminacion nocturna', 'portón'],
                'prioridad_base': 'alta',
                'area_responsable': 'Seguridad',
                'tiempo_respuesta': '2 horas'
            },
            'mantenimiento': {
                'keywords': ['reparacion', 'roto', 'arreglar', 'mantenimiento', 'pintura', 'jardin', 'limpieza'],
                'prioridad_base': 'media',
                'area_responsable': 'Mantenimiento',
                'tiempo_respuesta': '24 horas'
            },
            'iluminacion': {
                'keywords': ['luz', 'iluminacion', 'foco', 'lampara', 'alumbrado', 'oscuro'],
                'prioridad_base': 'media',
                'area_responsable': 'Mantenimiento Eléctrico',
                'tiempo_respuesta': '12 horas'
            },
            'espacios_comunes': {
                'keywords': ['quincho', 'pileta', 'cancha', 'playground', 'salon', 'espacio comun'],
                'prioridad_base': 'media',
                'area_responsable': 'Administración',
                'tiempo_respuesta': '48 horas'
            },
            'administracion': {
                'keywords': ['expensa', 'factura', 'pago', 'documento', 'administracion', 'consorcio'],
                'prioridad_base': 'baja',
                'area_responsable': 'Administración',
                'tiempo_respuesta': '72 horas'
            },
            'infraestructura': {
                'keywords': ['agua', 'gas', 'electricidad', 'cloaca', 'desague', 'fuga', 'corte'],
                'prioridad_base': 'alta',
                'area_responsable': 'Mantenimiento de Servicios',
                'tiempo_respuesta': '4 horas'
            }
        }
        
        self.urgencia_keywords = {
            'emergencia': ['emergencia', 'urgente', 'peligro', 'riesgo', 'accidente'],
            'alta': ['fuga', 'corte', 'robo', 'intruso', 'seguridad'],
            'media': ['roto', 'no funciona', 'problema'],
            'baja': ['consulta', 'solicitud', 'mejora', 'sugerencia']
        }

    def clasificar_reclamo(self, titulo, descripcion):
        """Clasifica automáticamente un reclamo"""
        texto_completo = f"{titulo} {descripcion}".lower()
        
        # Detectar categoría
        categoria_detectada = self._detectar_categoria(texto_completo)
        
        # Detectar prioridad
        prioridad_detectada = self._detectar_prioridad(texto_completo, categoria_detectada)
        
        # Generar sugerencias
        sugerencias = self._generar_sugerencias(categoria_detectada, prioridad_detectada)
        
        return {
            'categoria': categoria_detectada,
            'prioridad': prioridad_detectada,
            'area_responsable': self.categorias[categoria_detectada]['area_responsable'],
            'tiempo_respuesta': self.categorias[categoria_detectada]['tiempo_respuesta'],
            'sugerencias': sugerencias
        }

    def _detectar_categoria(self, texto):
        """Detecta la categoría del reclamo"""
        scores = {}
        
        for categoria, info in self.categorias.items():
            score = sum(1 for keyword in info['keywords'] if keyword in texto)
            if score > 0:
                scores[categoria] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return 'administracion'  # Por defecto

    def _detectar_prioridad(self, texto, categoria):
        """Detecta la prioridad del reclamo"""
        # Verificar palabras de urgencia
        for nivel, keywords in self.urgencia_keywords.items():
            if any(keyword in texto for keyword in keywords):
                if nivel == 'emergencia':
                    return 'emergencia'
                return nivel
        
        # Usar prioridad base de la categoría
        return self.categorias[categoria]['prioridad_base']

    def _generar_sugerencias(self, categoria, prioridad):
        """Genera sugerencias para el reclamo"""
        sugerencias = []
        
        if prioridad == 'emergencia':
            sugerencias.append("🚨 Este reclamo ha sido marcado como EMERGENCIA")
            sugerencias.append("📞 Contacta inmediatamente a seguridad: +54 11 4444-5556")
        
        if categoria == 'seguridad':
            sugerencias.append("🛡️ Asegúrate de estar en un lugar seguro")
            sugerencias.append("📸 Si es posible, toma fotos como evidencia")
        
        elif categoria == 'infraestructura':
            sugerencias.append("🔧 Cierra las llaves de paso si hay fuga de agua")
            sugerencias.append("⚡ No toques instalaciones eléctricas dañadas")
        
        elif categoria == 'mantenimiento':
            sugerencias.append("📷 Adjunta fotos del problema para acelerar la reparación")
            sugerencias.append("📍 Especifica la ubicación exacta del problema")
        
        return sugerencias

    def crear_respuesta_inteligente(self, clasificacion):
        """Crea una respuesta inteligente sobre la clasificación"""
        categoria = clasificacion['categoria']
        prioridad = clasificacion['prioridad']
        area = clasificacion['area_responsable']
        tiempo = clasificacion['tiempo_respuesta']
        
        emojis = {
            'seguridad': '🛡️',
            'mantenimiento': '🔧',
            'iluminacion': '💡',
            'espacios_comunes': '🏛️',
            'administracion': '📋',
            'infraestructura': '🔧'
        }
        
        prioridad_emojis = {
            'emergencia': '🚨',
            'alta': '🔴',
            'media': '🟡',
            'baja': '🟢'
        }
        
        response = f"""🤖 **Análisis Inteligente del Reclamo:**

{emojis.get(categoria, '📋')} **Categoría**: {categoria.replace('_', ' ').title()}
{prioridad_emojis.get(prioridad, '🟡')} **Prioridad**: {prioridad.title()}
👥 **Área Responsable**: {area}
⏱️ **Tiempo de Respuesta**: {tiempo}

"""
        
        if clasificacion['sugerencias']:
            response += "💡 **Sugerencias:**\n"
            for sugerencia in clasificacion['sugerencias']:
                response += f"• {sugerencia}\n"
        
        response += "\n✅ Tu reclamo ha sido clasificado automáticamente y derivado al área correspondiente."
        
        return response
