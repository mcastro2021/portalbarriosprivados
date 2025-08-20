# 🚀 Guía de Despliegue en Render

## Configuración Automática

El proyecto está configurado para desplegarse automáticamente en Render con los siguientes archivos:

### Archivos de Configuración
- `Procfile` - Define el comando de inicio
- `wsgi.py` - Punto de entrada WSGI
- `requirements.txt` - Dependencias de Python
- `runtime.txt` - Versión de Python
- `render.yaml` - Configuración de Render (opcional)

## Variables de Entorno Requeridas

### Básicas (Obligatorias)
- `SECRET_KEY` - Clave secreta de la aplicación
- `FLASK_ENV` - Entorno (production)
- `DATABASE_URL` - URL de la base de datos

### Opcionales
- `MAIL_SERVER` - Servidor SMTP
- `MAIL_USERNAME` - Usuario de email
- `MAIL_PASSWORD` - Contraseña de email
- `MERCADOPAGO_ACCESS_TOKEN` - Token de MercadoPago
- `TWILIO_ACCOUNT_SID` - SID de Twilio
- `OPENAI_API_KEY` - Clave de OpenAI
- `CLAUDE_API_KEY` - Clave de Claude

## Pasos para Desplegar

1. **Conectar repositorio** en Render
2. **Configurar variables de entorno** en el dashboard
3. **Deploy automático** se ejecutará

## Solución de Problemas

### Error 503
- Verificar que `wsgi.py` esté configurado correctamente
- Revisar logs en Render dashboard
- Verificar variables de entorno

### Error de Base de Datos
- Ejecutar `python init_db.py` localmente
- Verificar `DATABASE_URL` en variables de entorno

### Error de Dependencias
- Verificar `requirements.txt` esté actualizado
- Revisar versión de Python en `runtime.txt`

## Comandos Útiles

```bash
# Verificar configuración local
python wsgi.py

# Inicializar base de datos
python init_db.py

# Verificar dependencias
pip install -r requirements.txt
```

## Notas Importantes

- La aplicación usa SQLite por defecto
- SocketIO está configurado para funcionar sin Redis
- Las notificaciones por email requieren configuración SMTP
- El chatbot requiere claves de API de OpenAI o Claude
