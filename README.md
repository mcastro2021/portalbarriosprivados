# Portal de Barrio Cerrado - Sistema Integral

## Descripción
Sistema web completo para la gestión de barrios cerrados, incluyendo portal de visitas, reservas de espacios comunes, noticias, mantenimiento, pagos, clasificados, seguridad y más.

## Características Principales

### 🏠 Portal de Ingreso / Registro de Visitas
- Registro anticipado de visitas
- Generación automática de códigos QR
- Historial de ingresos/salidas
- Notificaciones en tiempo real
- Validación de documentos y vehículos

### 📅 Reserva de Espacios Comunes
- Quinchos, SUM, canchas, parrillas, coworking
- Calendario interactivo con disponibilidad
- Sistema de turnos y confirmaciones
- Notificaciones por email/WhatsApp

### 📢 Noticias y Comunicaciones
- Panel de novedades del barrio
- Alertas importantes (cortes, seguridad, obras)
- Envío automático por email y push
- Categorización de noticias

### 🔧 Reclamos y Mantenimiento
- Carga de reclamos con fotos
- Seguimiento del estado
- Comunicación con administración
- Sistema de prioridades

### 💳 Pagos y Estado de Expensas
- Consulta individual de expensas
- Integración con MercadoPago
- Historial de pagos
- Múltiples métodos de pago

### 🗺️ Mapa del Barrio
- Visualización por manzanas
- Información de calles
- Datos generales del barrio

### 📋 Anuncios Clasificados
- Compra-venta entre vecinos
- Ofertas de servicios
- Eventos sociales
- Sistema de contactos

### 🤖 Chatbot Inteligente
- Asistente virtual para consultas
- Respuestas automáticas
- Integración con todas las funcionalidades

### 🔒 Seguridad y Control
- Reportes de seguridad
- Botón de pánico
- Alertas comunitarias
- Control de accesos

## Tecnologías Utilizadas

### Backend
- **Python 3.9+**
- **Flask** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **Flask-Login** - Autenticación de usuarios
- **Flask-SocketIO** - Comunicación en tiempo real
- **Flask-Mail** - Envío de emails
- **MercadoPago SDK** - Procesamiento de pagos
- **QRCode** - Generación de códigos QR

### Frontend
- **HTML5/CSS3** - Estructura y estilos
- **JavaScript (ES6+)** - Interactividad
- **Bootstrap 5** - Framework CSS
- **Socket.IO** - WebSockets para tiempo real
- **Chart.js** - Gráficos y estadísticas
- **Leaflet.js** - Mapas interactivos

### Base de Datos
- **SQLite** (desarrollo)
- **PostgreSQL** (producción)

## Instalación y Configuración

### Requisitos Previos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd portalbarriosprivados
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Inicializar base de datos**
```bash
python init_db.py
```

**Nota**: Los datos de ejemplo solo se crean una vez. Si necesitas resetear la base de datos completamente, usa:
```bash
python reset_db.py
```

**Verificar estado de la base de datos**:
```bash
python check_db.py
```

6. **Ejecutar la aplicación**
```bash
python app.py
```

### Variables de Entorno (.env)

```env
# Configuración de la aplicación
SECRET_KEY=tu_clave_secreta_aqui
FLASK_ENV=development
DATABASE_URL=sqlite:///barrio_cerrado.db

# Configuración de email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password_de_aplicacion

# MercadoPago
MERCADOPAGO_ACCESS_TOKEN=TU_ACCESS_TOKEN_MERCADOPAGO

# Configuración de WhatsApp (opcional)
WHATSAPP_API_KEY=tu_api_key_whatsapp
WHATSAPP_PHONE_NUMBER=tu_numero_whatsapp
```

## Estructura del Proyecto

```
portalbarriosprivados/
├── app.py                 # Aplicación principal Flask
├── config.py             # Configuraciones
├── models.py             # Modelos de base de datos
├── routes/               # Rutas organizadas por módulo
│   ├── auth.py          # Autenticación
│   ├── visits.py        # Gestión de visitas
│   ├── reservations.py  # Reservas de espacios
│   ├── news.py          # Noticias
│   ├── maintenance.py   # Mantenimiento
│   ├── expenses.py      # Expensas y pagos
│   ├── classifieds.py   # Clasificados
│   ├── security.py      # Seguridad
│   └── chatbot.py       # Chatbot
├── static/              # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
├── templates/           # Plantillas HTML
├── uploads/            # Archivos subidos
├── utils/              # Utilidades
├── requirements.txt    # Dependencias
├── init_db.py         # Inicialización de BD
├── reset_db.py        # Reset completo de BD (solo desarrollo)
├── check_db.py        # Verificar estado de BD
├── test_bulk_delete.py # Prueba eliminación masiva
└── README.md          # Este archivo
```

## Funcionalidades Detalladas

### 1. Sistema de Usuarios
- **Roles**: Administrador, Residente, Seguridad
- **Registro** con validación de email
- **Perfiles** personalizables
- **Gestión de permisos** por rol
- **Acciones en lote**: Activar, desactivar, verificar emails, resetear contraseñas, eliminar múltiples usuarios

### 2. Gestión de Visitas
- **Registro anticipado** con validación
- **Códigos QR** únicos por visita
- **Notificaciones** automáticas
- **Historial completo** de visitas
- **Validación de documentos**

### 3. Reservas de Espacios
- **Calendario interactivo** con disponibilidad
- **Múltiples espacios**: quinchos, SUM, canchas
- **Sistema de aprobación** automática/manual
- **Notificaciones** de confirmación
- **Cancelaciones** con penalización

### 4. Sistema de Noticias
- **Editor rico** para contenido
- **Categorización** automática
- **Alertas importantes** destacadas
- **Envío masivo** de notificaciones
- **Archivo histórico**

### 5. Mantenimiento
- **Formularios detallados** con fotos
- **Sistema de prioridades**
- **Seguimiento de estado**
- **Comunicación bidireccional**
- **Reportes automáticos**

### 6. Gestión de Expensas
- **Cálculo automático** por mes
- **Múltiples métodos** de pago
- **Integración MercadoPago**
- **Comprobantes** descargables
- **Historial completo**

### 7. Clasificados
- **Categorías** predefinidas
- **Sistema de contactos**
- **Gestión de imágenes**
- **Búsqueda avanzada**
- **Moderación** de contenido

### 8. Seguridad
- **Reportes detallados**
- **Sistema de alertas**
- **Botón de pánico**
- **Notificaciones urgentes**
- **Historial de incidentes**

### 9. Chatbot Inteligente
- **Respuestas automáticas**
- **Integración** con todas las funciones
- **Aprendizaje** de patrones
- **Soporte 24/7**

## Despliegue

### Opciones de Hosting Gratuito

1. **Render** (Recomendado)
   - Deploy automático desde GitHub
   - Base de datos PostgreSQL incluida
   - SSL gratuito

2. **Railway**
   - Deploy rápido
   - Base de datos incluida
   - Escalabilidad automática

3. **Heroku**
   - Plataforma establecida
   - Add-ons disponibles
   - Documentación extensa

4. **PythonAnywhere**
   - Especializado en Python
   - SSL gratuito
   - Dominio personalizado

### Pasos para Despliegue en Render

1. **Crear cuenta en Render**
2. **Conectar repositorio GitHub**
3. **Configurar variables de entorno**
4. **Deploy automático**

## Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte técnico o consultas:
- Email: soporte@barrioprivado.com
- WhatsApp: +54 9 11 1234-5678
- Documentación: [docs.barrioprivado.com](https://docs.barrioprivado.com)

## Roadmap

### Versión 2.0
- [ ] App móvil nativa
- [ ] Integración con cámaras IP
- [ ] Sistema de encuestas
- [ ] Dashboard analítico avanzado
- [ ] API pública para desarrolladores

### Versión 2.1
- [ ] Inteligencia artificial para mantenimiento predictivo
- [ ] Sistema de votaciones electrónicas
- [ ] Integración con servicios municipales
- [ ] Módulo de contabilidad avanzado

---

**Desarrollado con ❤️ para mejorar la calidad de vida en barrios cerrados** 