#!/usr/bin/env python3
"""
Script para configurar la API key de Claude AI con la key existente
"""

import os

def configure_claude_api():
    """Configurar la API key de Claude AI"""
    print("🤖 Configurando Claude AI para el Chatbot")
    print("=" * 50)
    
    # API key que ya tenías (reemplaza con tu key real)
    api_key = "sk-ant-api03-YourActualAPIKeyHere"  # Reemplaza con tu key real
    
    # Verificar si la key es válida
    if not api_key or api_key == "sk-ant-api03-YourActualAPIKeyHere":
        print("❌ Por favor, reemplaza 'YourActualAPIKeyHere' con tu API key real de Claude")
        print("📋 Para obtener tu API key:")
        print("1. Ve a https://console.anthropic.com/")
        print("2. Crea una cuenta o inicia sesión")
        print("3. Ve a 'API Keys' en el menú")
        print("4. Crea una nueva API key")
        print("5. Copia la key (comienza con 'sk-ant-...')")
        return
    
    # Configurar variable de entorno
    os.environ['CLAUDE_API_KEY'] = api_key
    
    # Probar la configuración
    print("\n🧪 Probando configuración...")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        # Hacer una llamada de prueba simple
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hola"}]
        )
        print("✅ Conexión con Claude AI exitosa!")
        print("🤖 El chatbot ahora usará inteligencia artificial de Claude")
        
        # Probar una pregunta específica sobre reglamentos
        print("\n🧪 Probando pregunta sobre reglamentos...")
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=100,
            messages=[{"role": "user", "content": "¿Cuál es el reglamento de construcción en un barrio cerrado?"}]
        )
        print("✅ Respuesta de Claude:", response.content[0].text.strip())
        
    except Exception as e:
        print(f"❌ Error al probar la API key: {e}")
        print("Verifica que la API key sea correcta y tenga saldo disponible")

if __name__ == '__main__':
    configure_claude_api()
