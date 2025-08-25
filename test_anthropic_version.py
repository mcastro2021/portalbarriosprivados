#!/usr/bin/env python3
"""
Script para verificar la versión de anthropic y probar la inicialización del cliente
"""

import os

def test_anthropic():
    """Probar la versión de anthropic y la inicialización del cliente"""
    print("🧪 Probando versión de Anthropic")
    print("=" * 40)
    
    try:
        import anthropic
        print(f"✅ Versión de anthropic: {anthropic.__version__}")
        
        # Configurar API key
        api_key = "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"
        os.environ['CLAUDE_API_KEY'] = api_key
        
        print("🔧 Probando inicialización del cliente...")
        
        # Probar diferentes formas de inicializar el cliente
        try:
            client = anthropic.Anthropic(api_key=api_key)
            print("✅ Cliente inicializado correctamente con api_key=api_key")
        except Exception as e:
            print(f"❌ Error con api_key=api_key: {e}")
        
        try:
            client = anthropic.Anthropic(api_key)
            print("✅ Cliente inicializado correctamente con api_key directo")
        except Exception as e:
            print(f"❌ Error con api_key directo: {e}")
        
        # Probar una llamada simple
        try:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hola"}]
            )
            print("✅ Llamada a la API exitosa!")
            print(f"📝 Respuesta: {response.content[0].text.strip()}")
        except Exception as e:
            print(f"❌ Error en llamada a la API: {e}")
        
    except ImportError as e:
        print(f"❌ Error importando anthropic: {e}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == '__main__':
    test_anthropic()
