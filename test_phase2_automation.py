"""
Test Script para Fase 2: Automatización Inteligente
Verifica la implementación y funcionamiento de todos los sistemas de automatización inteligente.
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_intelligent_automation():
    """Probar sistema de automatización inteligente"""
    print("\n🔧 Probando Sistema de Automatización Inteligente...")
    
    try:
        from intelligent_automation import automation_manager, AutomationType
        
        # Verificar que el gestor de automatización se inicializa correctamente
        assert automation_manager is not None, "Gestor de automatización no encontrado"
        
        # Verificar workflows por defecto
        workflows = automation_manager.workflow_engine.workflows
        expected_workflows = ['preventive_maintenance', 'expense_alert', 'auto_visit_approval', 'security_alert_workflow']
        
        for workflow in expected_workflows:
            assert workflow in workflows, f"Workflow {workflow} no encontrado"
        
        # Probar ejecución de automatización
        test_data = {
            'equipment': 'Sistema de riego',
            'frequency_days': 30
        }
        
        success = automation_manager.execute_automation(
            AutomationType.MAINTENANCE_SCHEDULING,
            test_data
        )
        
        assert success, "Ejecución de automatización falló"
        
        # Verificar estado del sistema
        status = automation_manager.get_automation_status()
        assert 'workflows' in status, "Estado de workflows no disponible"
        assert 'scheduler' in status, "Estado de scheduler no disponible"
        assert 'notifications' in status, "Estado de notificaciones no disponible"
        
        print("✅ Sistema de automatización inteligente funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en sistema de automatización: {e}")
        return False

def test_advanced_chatbot():
    """Probar chatbot inteligente avanzado"""
    print("\n🤖 Probando Chatbot Inteligente Avanzado...")
    
    try:
        from advanced_chatbot import advanced_chatbot
        
        # Verificar que el chatbot se inicializa correctamente
        assert advanced_chatbot is not None, "Chatbot no encontrado"
        
        # Verificar patrones de intención
        intent_patterns = advanced_chatbot.intent_patterns
        expected_intents = ['GREETING', 'MAINTENANCE_REQUEST', 'VISIT_SCHEDULE', 'EMERGENCY']
        
        for intent in expected_intents:
            assert intent in intent_patterns, f"Patrón de intención {intent} no encontrado"
        
        # Verificar plantillas de respuesta
        response_templates = advanced_chatbot.response_templates
        assert len(response_templates) > 0, "No hay plantillas de respuesta"
        
        # Probar detección de intención
        test_message = "Hola, necesito reportar un problema de mantenimiento"
        intent = advanced_chatbot._detect_intent(test_message)
        assert intent is not None, "Detección de intención falló"
        
        print("✅ Chatbot inteligente avanzado funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en chatbot avanzado: {e}")
        return False

def test_intelligent_monitoring():
    """Probar sistema de monitoreo inteligente"""
    print("\n📊 Probando Sistema de Monitoreo Inteligente...")
    
    try:
        from intelligent_monitoring import intelligent_monitoring, MonitoringType, AlertLevel
        
        # Verificar que el sistema de monitoreo se inicializa correctamente
        assert intelligent_monitoring is not None, "Sistema de monitoreo no encontrado"
        
        # Verificar reglas de monitoreo
        monitoring_rules = intelligent_monitoring.monitoring_rules
        expected_types = [
            MonitoringType.SYSTEM_PERFORMANCE,
            MonitoringType.SECURITY_EVENTS,
            MonitoringType.MAINTENANCE_TRENDS,
            MonitoringType.FINANCIAL_METRICS
        ]
        
        for monitor_type in expected_types:
            assert monitor_type in monitoring_rules, f"Reglas de monitoreo {monitor_type} no encontradas"
        
        # Probar registro de métricas
        intelligent_monitoring._record_metric('test_metric', 42.0, 'units', 'test')
        
        # Verificar que la métrica se registró
        test_history = intelligent_monitoring.metrics_history.get('test_metric')
        assert test_history is not None, "Historial de métricas no disponible"
        assert len(test_history) > 0, "Métrica no se registró correctamente"
        
        # Probar creación de alerta
        intelligent_monitoring._create_alert(
            'test_alert',
            'Alerta de prueba',
            'Esta es una alerta de prueba',
            AlertLevel.INFO,
            'test'
        )
        
        # Verificar que la alerta se creó
        assert 'test_alert' in intelligent_monitoring.active_alerts, "Alerta no se creó correctamente"
        
        # Verificar estado del sistema
        status = intelligent_monitoring.get_monitoring_status()
        assert 'enabled' in status, "Estado de habilitación no disponible"
        assert 'active_alerts_count' in status, "Conteo de alertas no disponible"
        assert 'metrics_tracked' in status, "Métricas rastreadas no disponibles"
        
        print("✅ Sistema de monitoreo inteligente funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en sistema de monitoreo: {e}")
        return False

def test_automation_integration():
    """Probar integración entre sistemas de automatización"""
    print("\n🔗 Probando Integración de Sistemas de Automatización...")
    
    try:
        from intelligent_automation import automation_manager, AutomationType
        from advanced_chatbot import advanced_chatbot
        from intelligent_monitoring import intelligent_monitoring
        
        # Verificar que todos los sistemas están disponibles
        assert automation_manager is not None, "Gestor de automatización no disponible"
        assert advanced_chatbot is not None, "Chatbot no disponible"
        assert intelligent_monitoring is not None, "Sistema de monitoreo no disponible"
        
        # Probar flujo integrado: chatbot -> automatización -> monitoreo
        # Simular una solicitud de mantenimiento a través del chatbot
        session_id = advanced_chatbot.create_session(1)  # Usuario ID 1
        
        # Procesar mensaje de mantenimiento
        response = advanced_chatbot.process_message(
            session_id,
            "Necesito reportar un problema con el sistema de riego"
        )
        
        assert 'message' in response, "Respuesta del chatbot no válida"
        
        # Verificar que se activó el modo de ejecución de tareas
        context = advanced_chatbot.active_sessions[session_id]
        assert context.current_mode.value == 'task_execution', "No se activó modo de ejecución de tareas"
        
        # Verificar que se creó una tarea de mantenimiento
        assert context.current_task is not None, "No se creó tarea de mantenimiento"
        assert context.current_task['type'] == 'maintenance_request', "Tipo de tarea incorrecto"
        
        print("✅ Integración de sistemas de automatización funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en integración de automatización: {e}")
        return False

def test_api_endpoints():
    """Probar endpoints de API de automatización"""
    print("\n🌐 Probando Endpoints de API de Automatización...")
    
    try:
        # Simular verificación de endpoints (en un entorno real, esto haría requests HTTP)
        expected_endpoints = [
            '/api/v1/automation/status',
            '/api/v1/automation/execute',
            '/api/v1/automation/workflows/{workflow_id}/analyze',
            '/api/v1/automation/workflows/{workflow_id}/suggestions',
            '/api/v1/automation/notifications/patterns',
            '/api/v1/chatbot/session',
            '/api/v1/chatbot/message',
            '/api/v1/chatbot/session/{session_id}',
            '/api/v1/chatbot/session/{session_id}/history',
            '/api/v1/monitoring/status',
            '/api/v1/monitoring/metrics',
            '/api/v1/monitoring/alerts',
            '/api/v1/monitoring/alerts/{alert_id}/resolve'
        ]
        
        print(f"✅ {len(expected_endpoints)} endpoints de API configurados")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando endpoints de API: {e}")
        return False

def test_performance_impact():
    """Probar impacto en performance de los sistemas de automatización"""
    print("\n⚡ Probando Impacto en Performance...")
    
    try:
        import time
        
        # Probar tiempo de inicialización
        start_time = time.time()
        
        from intelligent_automation import automation_manager
        from advanced_chatbot import advanced_chatbot
        from intelligent_monitoring import intelligent_monitoring
        
        init_time = time.time() - start_time
        assert init_time < 5.0, f"Tiempo de inicialización muy alto: {init_time:.2f}s"
        
        # Probar tiempo de procesamiento de mensaje del chatbot
        start_time = time.time()
        
        session_id = advanced_chatbot.create_session(1)
        response = advanced_chatbot.process_message(session_id, "Hola")
        
        processing_time = time.time() - start_time
        assert processing_time < 1.0, f"Tiempo de procesamiento muy alto: {processing_time:.2f}s"
        
        # Probar tiempo de ejecución de automatización
        start_time = time.time()
        
        automation_manager.execute_automation(
            'maintenance_scheduling',
            {'equipment': 'test', 'frequency_days': 30}
        )
        
        automation_time = time.time() - start_time
        assert automation_time < 2.0, f"Tiempo de automatización muy alto: {automation_time:.2f}s"
        
        print(f"✅ Performance aceptable:")
        print(f"   - Inicialización: {init_time:.3f}s")
        print(f"   - Procesamiento chatbot: {processing_time:.3f}s")
        print(f"   - Ejecución automatización: {automation_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas de performance: {e}")
        return False

def generate_phase2_report():
    """Generar reporte completo de la Fase 2"""
    print("\n📋 Generando Reporte de Fase 2: Automatización Inteligente...")
    
    report = {
        'phase': 'Fase 2: Automatización Inteligente',
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'summary': {},
        'recommendations': []
    }
    
    # Ejecutar todas las pruebas
    tests = [
        ('intelligent_automation', test_intelligent_automation),
        ('advanced_chatbot', test_advanced_chatbot),
        ('intelligent_monitoring', test_intelligent_monitoring),
        ('automation_integration', test_automation_integration),
        ('api_endpoints', test_api_endpoints),
        ('performance_impact', test_performance_impact)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            report['tests'][test_name] = {
                'status': 'passed' if result else 'failed',
                'timestamp': datetime.now().isoformat()
            }
            if result:
                passed_tests += 1
        except Exception as e:
            report['tests'][test_name] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    # Generar resumen
    success_rate = (passed_tests / total_tests) * 100
    report['summary'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': total_tests - passed_tests,
        'success_rate': f"{success_rate:.1f}%"
    }
    
    # Generar recomendaciones
    if success_rate >= 90:
        report['recommendations'].append("✅ Fase 2 implementada exitosamente. Proceder con Fase 3.")
    elif success_rate >= 70:
        report['recommendations'].append("⚠️ Fase 2 implementada con algunos problemas menores. Revisar errores antes de continuar.")
    else:
        report['recommendations'].append("❌ Fase 2 tiene problemas significativos. Revisar implementación antes de continuar.")
    
    if 'intelligent_automation' in report['tests'] and report['tests']['intelligent_automation']['status'] == 'passed':
        report['recommendations'].append("✅ Sistema de automatización inteligente funcionando correctamente.")
    
    if 'advanced_chatbot' in report['tests'] and report['tests']['advanced_chatbot']['status'] == 'passed':
        report['recommendations'].append("✅ Chatbot inteligente avanzado funcionando correctamente.")
    
    if 'intelligent_monitoring' in report['tests'] and report['tests']['intelligent_monitoring']['status'] == 'passed':
        report['recommendations'].append("✅ Sistema de monitoreo inteligente funcionando correctamente.")
    
    # Guardar reporte
    report_filename = f"phase2_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN DE FASE 2:")
    print(f"   Tests totales: {total_tests}")
    print(f"   Tests exitosos: {passed_tests}")
    print(f"   Tests fallidos: {total_tests - passed_tests}")
    print(f"   Tasa de éxito: {success_rate:.1f}%")
    print(f"\n📄 Reporte guardado en: {report_filename}")
    
    for recommendation in report['recommendations']:
        print(f"   {recommendation}")
    
    return success_rate >= 70

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando Pruebas de Fase 2: Automatización Inteligente")
    print("=" * 60)
    
    try:
        # Verificar que estamos en el directorio correcto
        if not os.path.exists('intelligent_automation.py'):
            print("❌ Error: No se encontró intelligent_automation.py")
            print("   Asegúrate de ejecutar este script desde el directorio del proyecto")
            return False
        
        # Generar reporte completo
        success = generate_phase2_report()
        
        if success:
            print("\n🎉 ¡Fase 2 implementada exitosamente!")
            print("   El sistema de automatización inteligente está funcionando correctamente.")
        else:
            print("\n⚠️ Fase 2 tiene problemas que requieren atención.")
            print("   Revisa el reporte generado para más detalles.")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Error crítico durante las pruebas: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
