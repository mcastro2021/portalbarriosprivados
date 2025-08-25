# 🚀 Guía de Despliegue - Portal Barrios Privados

## 📋 Problema Resuelto

**Error Original:**
```
AttributeError: module 'app' has no attribute 'app'
gunicorn.errors.AppImportError: Failed to find attribute 'app' in 'app'.
```

**Solución Implementada:**
- ✅ Archivo WSGI separado (`wsgi.py`) para Gunicorn
- ✅ Manejo robusto de errores de importación
- ✅ Aplicación de fallback en caso de errores
- ✅ Configuración específica para Render

## 🔧 Archivos de Despliegue

### 1. `wsgi.py` - Entry Point para Gunicorn
```python
# Archivo WSGI robusto con manejo de errores
application = create_application()
app = application  # Alias para compatibilidad
```

### 2. `render.yaml` - Configuración de Render
```yaml
services:
  - type: web
    name: portal-barrios-privados
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## 🚀 Comandos de Despliegue

### Opción 1: Usar archivo WSGI (Recomendado)
```bash
# Para Render o producción
gunicorn wsgi:application

# Con configuración específica
gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### Opción 2: Usar app.py directamente (Fallback)
```bash
# Si wsgi.py no funciona
gunicorn app:app
```

### Opción 3: Desarrollo local
```bash
# Ejecutar directamente
python wsgi.py

# O usar Flask
python app.py
```

## 🔍 Diagnóstico de Problemas

### 1. Script de Prueba Automático (NUEVO)
```bash
# Ejecutar script de diagnóstico completo
python test_wsgi.py

# Este script verifica:
# - Dependencias críticas
# - Importación de app.py
# - Configuración WSGI
# - Endpoint /health
```

### 2. Verificar Importaciones Manualmente
```bash
# Probar importaciones manualmente
python -c "from app import create_app; print('✅ Importación exitosa')"
python -c "from wsgi import application; print('✅ WSGI exitoso')"
```

### 2. Verificar Dependencias
```bash
# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list | grep -E "(Flask|gunicorn)"
```

### 3. Verificar Health Check
```bash
# Probar endpoint de salud
curl http://localhost:5000/health

# Respuesta esperada:
# {"status": "healthy", "timestamp": "...", "database": "OK"}
```

## 🛠️ Configuración de Variables de Entorno

### Variables Requeridas
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export DATABASE_URL=sqlite:///instance/database.db
```

### Variables Opcionales
```bash
export PYTHONPATH=.
export PORT=5000
export WORKERS=2
```

## 📁 Estructura de Archivos Críticos

```
portalbarriosprivados/
├── wsgi.py                 # ✅ Entry point para Gunicorn
├── app.py                  # ✅ Aplicación Flask principal
├── render.yaml             # ✅ Configuración de Render
├── requirements.txt        # ✅ Dependencias actualizadas
├── test_wsgi.py           # ✅ Script de diagnóstico WSGI
├── config.py              # Configuración de la app
├── models.py              # Modelos de base de datos
└── app/                   # Servicios y mejoras implementadas
    ├── core/
    │   ├── error_handler.py
    │   ├── logging_service.py
    │   ├── monitoring_service.py
    │   ├── database_optimizer.py
    │   ├── backup_service.py
    │   └── testing_service.py
    ├── services/
    │   └── two_factor_service.py
    └── schemas/
        └── validation_schemas.py
```

## 🎯 Verificación de Despliegue

### 1. Endpoints Críticos
```bash
# Health check
curl https://your-app.onrender.com/health

# API test
curl https://your-app.onrender.com/api/ping

# Página principal
curl https://your-app.onrender.com/
```

### 2. Logs de Aplicación
```bash
# Ver logs en Render
# Dashboard > Service > Logs

# Buscar estos mensajes:
# ✅ Aplicación Flask creada correctamente para WSGI
# ✅ Base de datos inicializada correctamente
# ✅ Servicio de logging inicializado
```

## 🚨 Solución de Problemas Comunes

### Error: "Failed to find attribute 'app'"
**Solución:** Usar `wsgi:application` en lugar de `app:app`
```bash
gunicorn wsgi:application
```

### Error: "ModuleNotFoundError"
**Solución:** Verificar PYTHONPATH y estructura de archivos
```bash
export PYTHONPATH=.
python -c "import app; print('OK')"
```

### Error: "Database connection failed"
**Solución:** Verificar configuración de base de datos
```bash
# Crear directorio instance
mkdir -p instance

# Verificar permisos
ls -la instance/
```

### Error: "Import errors in routes"
**Solución:** El archivo WSGI maneja esto con aplicación de fallback
- La aplicación seguirá funcionando con funcionalidad básica
- Los errores se mostrarán en `/health`

## 📊 Monitoreo Post-Despliegue

### 1. Health Checks Automáticos
- Render verificará `/health` automáticamente
- Respuesta esperada: `{"status": "healthy"}`

### 2. Métricas Disponibles
```bash
# Estadísticas de la aplicación
curl https://your-app.onrender.com/api/stats

# Conteo de notificaciones
curl https://your-app.onrender.com/api/notifications/count
```

### 3. Logs Estructurados
- Los logs se guardan en `logs/barrio_cerrado.log`
- Formato JSON para fácil análisis
- Rotación automática de archivos

## 🎉 Resultado Final

Con esta configuración:
- ✅ **Despliegue exitoso** en Render
- ✅ **Manejo robusto de errores** de importación
- ✅ **Aplicación de fallback** en caso de problemas
- ✅ **Health checks** funcionando
- ✅ **8 mejoras críticas** implementadas y funcionando
- ✅ **Monitoreo y logging** completo

El sistema está **listo para producción** con todas las mejoras implementadas.
