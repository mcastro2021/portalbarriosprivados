#!/usr/bin/env python3
"""
Script para probar el chatbot con preguntas específicas
"""

import os
import sys

def test_chatbot():
    """Probar el chatbot con preguntas específicas"""
    print("🤖 Probando Chatbot con Preguntas Específicas")
    print("=" * 50)
    
    # Configurar variable de entorno para Claude (reemplaza con tu key real)
    api_key = "sk-ant-api03-YourActualAPIKeyHere"  # Reemplaza con tu key real
    
    if api_key == "sk-ant-api03-YourActualAPIKeyHere":
        print("❌ Por favor, configura tu API key de Claude en el script")
        return
    
    os.environ['CLAUDE_API_KEY'] = api_key
    
    # Preguntas de prueba
    test_questions = [
        "¿Cuál es el reglamento de construcción?",
        "¿Qué horarios están permitidos para construcción?",
        "¿Necesito autorización para hacer una reforma?",
        "¿Cuál es la altura máxima permitida?",
        "¿Qué materiales están permitidos?"
    ]
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        # Cargar reglamentos
        try:
            with open('REGLAMENTOS_BARRIO.md', 'r', encoding='utf-8') as f:
                reglamentos_content = f.read()
        except FileNotFoundError:
            reglamentos_content = "Reglamentos no disponibles"
        
        # Prompt del sistema
        system_prompt = f"""Eres un asistente virtual especializado para un barrio cerrado privado llamado "Barrio Tejas 4". 

CONOCIMIENTO ESPECÍFICO DEL BARRIO:
- Horarios: Administración (Lun-Vie 9-17h), Seguridad (24/7), Quincho (10-22h)
- Contactos: Administración (+54 11 4444-5555), Seguridad (+54 11 4444-5556)
- Espacios comunes: Quincho principal, Quincho pequeño, SUM, Cancha de fútbol, Cancha de tenis, Piscina, Espacio coworking

REGLAMENTOS Y NORMAS COMPLETAS DEL BARRIO:

{reglamentos_content}

INSTRUCCIONES:
1. SIEMPRE responde basándote en los reglamentos específicos del barrio
2. Si te preguntan sobre reglamentos constructivos, usa la información del archivo de reglamentos
3. Proporciona información precisa y actualizada
4. Si no encuentras información específica, indícalo claramente
5. Ser muy específico con reglamentos y procedimientos
6. Citar secciones específicas de reglamentos cuando sea relevante

ESTILO DE RESPUESTA:
- Amigable y profesional
- Respuestas concisas pero informativas
- Usar emojis apropiados
- Ser muy específico con reglamentos y procedimientos
- Citar secciones específicas de reglamentos cuando sea relevante"""

        print("🧪 Probando preguntas sobre reglamentos de construcción...")
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Pregunta: {question}")
            print("-" * 40)
            
            try:
                response = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    messages=[
                        {"role": "user", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                
                answer = response.content[0].text.strip()
                print(f"✅ Respuesta: {answer}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n🎉 Pruebas completadas!")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == '__main__':
    test_chatbot()
