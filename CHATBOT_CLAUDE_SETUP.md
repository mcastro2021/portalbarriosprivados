# 🤖 Chatbot con Claude API - Configuración

## 📋 Descripción

El chatbot del portal de barrios privados ahora utiliza la **API de Claude** como sistema principal de inteligencia artificial, reemplazando las respuestas automáticas predefinidas con respuestas más inteligentes y contextuales.

## 🚀 Características

- **Claude como IA principal**: Usa Claude 3 Sonnet para generar respuestas inteligentes
- **Contexto del barrio**: Conocimiento específico sobre reglamentos, horarios, servicios
- **Historial de conversación**: Mantiene contexto de conversaciones previas
- **Fallback inteligente**: Si Claude no está disponible, usa OpenAI GPT como respaldo
- **Base de conocimiento**: Mantiene respuestas específicas para consultas comunes

## ⚙️ Configuración

### 1. Obtener API Key de Claude

1. Ve a [console.anthropic.com](https://console.anthropic.com)
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys" en el menú lateral
4. Crea una nueva API key
5. Copia la key (comienza con `sk-ant-...`)

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con:

```bash
# Claude API (prioridad alta)
CLAUDE_API_KEY=sk-ant-your-api-key-here
CLAUDE_MODEL=claude-3-sonnet-20240229

# OpenAI API (respaldo)
OPENAI_API_KEY=sk-your-openai-key-here
```

### 3. Instalar Dependencias

```bash
pip install anthropic==0.18.1
```

O actualizar requirements.txt:

```bash
pip install -r requirements.txt
```

## 🔄 Flujo de Procesamiento

El chatbot ahora sigue este orden de prioridad:

1. **Claude API** (nueva prioridad)
   - Analiza el mensaje con contexto del barrio
   - Usa historial de conversación
   - Genera respuesta inteligente y contextual

2. **Base de Conocimiento** (segunda prioridad)
   - Respuestas específicas para reglamentos
   - Información de contacto y horarios
   - Procedimientos del barrio

3. **Consultas de Datos** (tercera prioridad)
   - Estado de expensas
   - Visitas pendientes
   - Reservas confirmadas

4. **Clasificación de Reclamos** (cuarta prioridad)
   - Análisis inteligente de problemas
   - Clasificación por prioridad y área

5. **Respuestas por Palabras Clave** (quinta prioridad)
   - Redirecciones automáticas
   - Navegación por el sistema

6. **OpenAI GPT** (último recurso)
   - Solo si Claude no está disponible

## 🎯 Ejemplos de Uso

### Consultas Generales
```
Usuario: "¿Cuál es el horario de administración?"
Claude: "🏢 El horario de administración es de Lunes a Viernes de 9:00 a 17:00 horas. Para consultas fuera de este horario, puedes contactar a seguridad que está disponible 24/7 al +54 11 4444-5556."
```

### Consultas Contextuales
```
Usuario: "Tengo un problema con la iluminación de mi manzana"
Claude: "💡 Entiendo que tienes un problema con la iluminación. Esto sería un reclamo de mantenimiento de prioridad media. Te recomiendo crear un reclamo formal en la sección de Mantenimiento para que podamos darle seguimiento. ¿Quieres que te ayude a crear el reclamo?"
```

### Consultas Personales
```
Usuario: "¿Cuándo vence mi próxima expensa?"
Claude: "🔒 Para consultar el estado específico de tus expensas necesitas estar autenticado. Una vez que inicies sesión, podré mostrarte exactamente cuándo vence tu próxima expensa y el monto a pagar."
```

## 🔧 Configuración Avanzada

### Modelos Disponibles

Puedes cambiar el modelo de Claude modificando `CLAUDE_MODEL`:

- `claude-3-sonnet-20240229` (recomendado - balance entre velocidad y calidad)
- `claude-3-haiku-20240307` (más rápido, menos costoso)
- `claude-3-opus-20240229` (más lento, mayor calidad)

### Personalización del Prompt

El prompt del sistema incluye:
- Información del usuario (nombre, rol, autenticación)
- Conocimiento específico del barrio
- Historial de conversación
- Instrucciones de estilo y comportamiento

### Monitoreo y Logs

Los errores de la API de Claude se registran en la consola:
```python
print(f"Error en Claude API: {str(e)}")
```

## 💰 Costos

- **Claude 3 Sonnet**: ~$0.003 por 1K tokens de entrada, ~$0.015 por 1K tokens de salida
- **Claude 3 Haiku**: ~$0.00025 por 1K tokens de entrada, ~$0.00125 por 1K tokens de salida
- **Claude 3 Opus**: ~$0.015 por 1K tokens de entrada, ~$0.075 por 1K tokens de salida

## 🚨 Solución de Problemas

### Error: "No module named 'anthropic'"
```bash
pip install anthropic==0.18.1
```

### Error: "Invalid API key"
- Verifica que la API key comience con `sk-ant-`
- Asegúrate de que la key esté activa en la consola de Anthropic

### Claude no responde
- Verifica la conexión a internet
- Revisa los logs de error en la consola
- El sistema automáticamente usará OpenAI como respaldo

### Respuestas muy largas
- Ajusta `max_tokens` en la función `handle_claude_query`
- Actualmente configurado en 500 tokens

## 📞 Soporte

Para problemas específicos con la API de Claude:
- [Documentación oficial de Claude](https://docs.anthropic.com/)
- [Console de Anthropic](https://console.anthropic.com/)
- [Estado de la API](https://status.anthropic.com/)

---

**Nota**: El chatbot mantiene compatibilidad con OpenAI como respaldo, por lo que si Claude no está disponible, seguirá funcionando con GPT.
