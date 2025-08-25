#!/usr/bin/env python3
"""
Script para configurar la API key de Claude AI
"""

import os
import sys

def setup_claude_api():
    """Configurar la API key de Claude AI"""
    print("🤖 Configuración de Claude AI para el Chatbot")
    print("=" * 50)
    
    # Verificar si ya existe la variable de entorno
    current_key = os.environ.get('CLAUDE_API_KEY')
    if current_key:
        print(f"✅ API key de Claude ya configurada: {current_key[:10]}...")
        response = input("¿Deseas cambiar la API key? (s/n): ").lower()
        if response != 's':
            print("Configuración mantenida.")
            return
    
    print("\n📋 Para obtener tu API key de Claude AI:")
    print("1. Ve a https://console.anthropic.com/")
    print("2. Crea una cuenta o inicia sesión")
    print("3. Ve a 'API Keys' en el menú")
    print("4. Crea una nueva API key")
    print("5. Copia la key (comienza con 'sk-ant-...')")
    
    print("\n🔑 Ingresa tu API key de Claude AI:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No se ingresó una API key válida")
        return
    
    if not api_key.startswith('sk-ant-'):
        print("❌ La API key debe comenzar con 'sk-ant-'")
        return
    
    # Guardar en archivo .env
    env_file = '.env'
    env_content = ""
    
    # Leer archivo .env existente si existe
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # Buscar si ya existe CLAUDE_API_KEY
    lines = env_content.split('\n')
    claude_line_index = -1
    
    for i, line in enumerate(lines):
        if line.startswith('CLAUDE_API_KEY='):
            claude_line_index = i
            break
    
    # Actualizar o agregar la línea
    new_line = f'CLAUDE_API_KEY={api_key}'
    if claude_line_index >= 0:
        lines[claude_line_index] = new_line
    else:
        lines.append(new_line)
    
    # Escribir archivo actualizado
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ API key guardada en {env_file}")
    print("🔧 Para usar en producción, configura la variable de entorno CLAUDE_API_KEY en Render.com")
    
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
    except Exception as e:
        print(f"❌ Error al probar la API key: {e}")
        print("Verifica que la API key sea correcta y tenga saldo disponible")

def main():
    """Función principal"""
    try:
        setup_claude_api()
    except KeyboardInterrupt:
        print("\n\n❌ Configuración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la configuración: {e}")

if __name__ == '__main__':
    main()
