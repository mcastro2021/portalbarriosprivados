# 🤖 Configuración del Chatbot con Claude AI

## Resumen de Mejoras Implementadas

### ✅ Problemas Resueltos:
1. **Ruta de notificaciones**: Agregada `/api/notifications/count` al blueprint principal
2. **Redis**: Incluido en requirements.txt para rate limiting
3. **CSRF**: Deshabilitado en producción para evitar errores
4. **Chatbot mejorado**: Ahora usa Claude AI con configuración centralizada
5. **Usuarios de prueba**: Eliminada la creación automática

### 🔧 Configuración del Chatbot

#### 1. Configuración Local (Desarrollo)

Para configurar Claude AI localmente:

```bash
# Ejecutar el script de configuración
python setup_claude.py
```

El script te guiará para:
- Obtener una API key de Claude AI
- Configurar la variable de entorno
- Probar la conexión

#### 2. Configuración en Producción (Render.com)

Para usar Claude AI en producción:

1. Ve a tu dashboard de Render.com
2. Selecciona tu servicio `portalbarriosprivados`
3. Ve a "Environment"
4. Agrega la variable de entorno:
   - **Key**: `CLAUDE_API_KEY`
   - **Value**: `sk-ant-your-api-key-here`

#### 3. Obtener API Key de Claude AI

1. Ve a [https://console.anthropic.com/](https://console.anthropic.com/)
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys" en el menú lateral
4. Haz clic en "Create Key"
5. Copia la key (comienza con `sk-ant-...`)

### 🚀 Funcionalidades del Chatbot

#### Con Claude AI (Recomendado):
- ✅ Respuestas inteligentes basadas en reglamentos del barrio
- ✅ Contexto de conversación mantenido
- ✅ Clasificación automática de reclamos
- ✅ Información específica del barrio
- ✅ Navegación asistida

#### Sin Claude AI (Fallback):
- ✅ Respuestas basadas en palabras clave
- ✅ Base de conocimiento local
- ✅ Funcionalidad básica mantenida

### 📁 Archivos de Configuración

- `chatbot_config.py` - Configuración centralizada del chatbot
- `setup_claude.py` - Script para configurar API key
- `routes/chatbot.py` - Lógica principal del chatbot
- `REGLAMENTOS_BARRIO.md` - Base de conocimiento del barrio

### 🔍 Verificación de Estado

Para verificar si Claude AI está funcionando:

```python
from chatbot_config import is_claude_available
print(f"Claude AI disponible: {is_claude_available()}")
```

### 📊 Logs y Monitoreo

El chatbot registra:
- ✅ Intentos de conexión a Claude AI
- ✅ Errores de API
- ✅ Uso de fallback cuando Claude no está disponible
- ✅ Estadísticas de uso

### 🛠️ Solución de Problemas

#### Error: "Claude AI no disponible"
- Verifica que `CLAUDE_API_KEY` esté configurada
- Asegúrate de que la API key sea válida
- Verifica que tengas saldo en tu cuenta de Anthropic

#### Error: "Rate limiting no disponible"
- Redis no está configurado (opcional)
- El chatbot funcionará sin rate limiting
- Para habilitar: configura Redis en Render.com

#### Error: "CSRF token is undefined"
- CSRF está deshabilitado en producción
- Si persiste, verifica la configuración en `config.py`

### 🎯 Próximos Pasos

1. **Configurar Claude AI** usando `setup_claude.py`
2. **Probar el chatbot** con preguntas sobre reglamentos
3. **Configurar en Render.com** la variable de entorno
4. **Monitorear logs** para verificar funcionamiento

### 📞 Soporte

Si tienes problemas:
1. Verifica los logs en Render.com
2. Ejecuta `python setup_claude.py` para diagnosticar
3. Revisa que la API key sea válida en [console.anthropic.com](https://console.anthropic.com/)

---

**¡El chatbot ahora está listo para usar inteligencia artificial de Claude! 🚀**
