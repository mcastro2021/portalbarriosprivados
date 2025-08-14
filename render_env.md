# Variables de Entorno para Render.com

Configura estas variables de entorno en tu servicio de Render.com:

## Variables Obligatorias

```
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
DATABASE_URL=postgresql://username:password@hostname:port/database
```

## Variables Opcionales (Recomendadas)

```
# Configuración de email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-app-password
MAIL_DEFAULT_SENDER=tu-email@gmail.com

# Configuración del barrio
BARRIO_NAME=Tu Barrio Privado
BARRIO_ADDRESS=Dirección del barrio
BARRIO_PHONE=+54 9 11 1234-5678
BARRIO_EMAIL=info@tubarrio.com

# Servicios externos (opcionales)
OPENAI_API_KEY=sk-...
MERCADOPAGO_ACCESS_TOKEN=APP_USR-...
MERCADOPAGO_PUBLIC_KEY=APP_USR-...
TWILIO_ACCOUNT_SID=ACxxxxxx
TWILIO_AUTH_TOKEN=xxxxxx
TWILIO_PHONE_NUMBER=+1234567890

# Redis (para cache y tareas en background)
REDIS_URL=redis://red-xxxxx:6379

# Configuración de notificaciones
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_WHATSAPP_ENABLED=false
NOTIFICATION_PUSH_ENABLED=true
```

## Configuración Recomendada en Render

1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --threads 2 app:app`
3. **Environment**: Python 3.13
4. **Plan**: Starter (512MB RAM mínimo)

### Alternativa con archivo de configuración
Si prefieres usar el archivo de configuración:
**Start Command**: `gunicorn -c gunicorn.conf.py app:app`

### Nota sobre Python 3.13
- **eventlet** no es compatible con Python 3.13 (problema con distutils)
- Usamos workers **sync** con threads para manejar concurrencia
- **SocketIO** configurado en modo **threading** en lugar de eventlet

## Base de Datos

Recomendamos usar PostgreSQL en lugar de SQLite para producción:
- Crea una base de datos PostgreSQL en Render
- Usa la DATABASE_URL proporcionada por Render
- La aplicación manejará automáticamente las migraciones
