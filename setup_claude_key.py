#!/usr/bin/env python3
"""
Script para configurar la API key de Claude AI fácilmente
"""

import os

def setup_claude_key():
    """Configurar la API key de Claude AI"""
    print("🤖 Configuración Rápida de Claude AI")
    print("=" * 40)
    
    # Aquí puedes poner tu API key real
    # Reemplaza "TU_API_KEY_AQUI" con tu key real de Claude
    api_key = "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"  # ← Reemplaza con tu key real
    
    if api_key == "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":
        print("❌ Por favor, edita este archivo y reemplaza 'TU_API_KEY_AQUI' con tu API key real")
        print("\n📋 Para obtener tu API key:")
        print("1. Ve a https://console.anthropic.com/")
        print("2. Crea una cuenta o inicia sesión")
        print("3. Ve a 'API Keys' en el menú")
        print("4. Crea una nueva API key")
        print("5. Copia la key (comienza con 'sk-ant-...')")
        print("\n🔧 Luego edita este archivo y reemplaza 'TU_API_KEY_AQUI' con tu key")
        return False
    
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
        
        print("\n🎉 ¡Configuración completada exitosamente!")
        print("🚀 El chatbot ahora funcionará con Claude AI")
        return True
        
    except Exception as e:
        print(f"❌ Error al probar la API key: {e}")
        print("Verifica que la API key sea correcta y tenga saldo disponible")
        return False

if __name__ == '__main__':
    setup_claude_key()
