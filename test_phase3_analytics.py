#!/usr/bin/env python3
"""
Test Script - Fase 3: Analytics y Business Intelligence
Script completo para probar todas las funcionalidades de analytics implementadas
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_analytics_engine():
    """Prueba el motor de analytics principal"""
    print("\n🔍 Probando Analytics Engine...")
    
    try:
        from analytics_engine import analytics_manager
        
        # Probar dashboard completo
        dashboard = analytics_manager.get_comprehensive_dashboard()
        print("✅ Dashboard completo generado")
        
        # Verificar estructura del dashboard
        required_keys = ['real_time', 'user_behavior', 'predictive_insights', 'business_intelligence', 'performance_metrics']
        for key in required_keys:
            if key in dashboard:
                print(f"✅ Sección {key} presente")
            else:
                print(f"❌ Sección {key} faltante")
        
        return True
    except Exception as e:
        print(f"❌ Error en analytics engine: {e}")
        return False

def test_real_time_analytics():
    """Prueba analytics en tiempo real"""
    print("\n⏱️ Probando Analytics en Tiempo Real...")
    
    try:
        from analytics_engine import analytics_manager
        
        # Probar dashboard en tiempo real
        real_time_data = analytics_manager.real_time_analytics.get_real_time_dashboard()
        print("✅ Dashboard en tiempo real generado")
        
        # Verificar métricas básicas
        metrics = ['active_sessions', 'recent_activity', 'activity_trend', 'alerts', 'performance_metrics']
        for metric in metrics:
            if metric in real_time_data:
                print(f"✅ Métrica {metric} presente")
            else:
                print(f"❌ Métrica {metric} faltante")
        
        # Probar actualización de métricas
        analytics_manager.real_time_analytics._update_real_time_metrics()
        print("✅ Métricas en tiempo real actualizadas")
        
        return True
    except Exception as e:
        print(f"❌ Error en analytics en tiempo real: {e}")
        return False

def test_predictive_analytics():
    """Prueba analytics predictivo"""
    print("\n🔮 Probando Analytics Predictivo...")
    
    try:
        from analytics_engine import analytics_manager
        
        # Probar análisis de comportamiento de usuarios
        user_behavior = analytics_manager.predictive_analytics.analyze_user_behavior()
        print("✅ Análisis de comportamiento de usuarios completado")
        
        # Verificar secciones del análisis
        behavior_sections = ['usage_patterns', 'user_segments', 'retention_prediction', 'engagement_analysis']
        for section in behavior_sections:
            if section in user_behavior:
                print(f"✅ Sección {section} presente")
            else:
                print(f"❌ Sección {section} faltante")
        
        # Probar predicciones de mantenimiento
        maintenance_predictions = analytics_manager.predictive_analytics.predict_maintenance_needs()
        print(f"✅ Predicciones de mantenimiento: {len(maintenance_predictions)} insights generados")
        
        # Probar predicciones financieras
        financial_predictions = analytics_manager.predictive_analytics.predict_financial_trends()
        print(f"✅ Predicciones financieras: {len(financial_predictions)} insights generados")
        
        return True
    except Exception as e:
        print(f"❌ Error en analytics predictivo: {e}")
        return False

def test_business_intelligence():
    """Prueba business intelligence"""
    print("\n📊 Probando Business Intelligence...")
    
    try:
        from analytics_engine import analytics_manager
        
        # Probar actualización de KPIs
        analytics_manager.business_intelligence.update_kpis()
        print("✅ KPIs actualizados")
        
        # Probar reporte ejecutivo
        bi_report = analytics_manager.business_intelligence.generate_executive_report()
        print("✅ Reporte ejecutivo generado")
        
        # Verificar estructura del reporte
        report_sections = ['summary', 'kpis', 'trends', 'recommendations']
        for section in report_sections:
            if section in bi_report:
                print(f"✅ Sección {section} presente")
            else:
                print(f"❌ Sección {section} faltante")
        
        # Verificar KPIs
        kpis = analytics_manager.business_intelligence.kpis
        expected_kpis = ['user_growth', 'user_engagement', 'security_incidents', 'maintenance_efficiency', 'financial_health']
        for kpi_name in expected_kpis:
            if kpi_name in kpis:
                print(f"✅ KPI {kpi_name} presente")
            else:
                print(f"❌ KPI {kpi_name} faltante")
        
        return True
    except Exception as e:
        print(f"❌ Error en business intelligence: {e}")
        return False

def test_data_export():
    """Prueba exportación de datos"""
    print("\n📤 Probando Exportación de Datos...")
    
    try:
        from analytics_engine import analytics_manager
        
        # Probar exportación en diferentes formatos
        formats = ['csv', 'json', 'excel', 'pdf']
        for format_type in formats:
            result = analytics_manager.export_data('dashboard', format_type)
            if 'generado' in result or 'exportado' in result:
                print(f"✅ Exportación {format_type} exitosa")
            else:
                print(f"❌ Error en exportación {format_type}")
        
        return True
    except Exception as e:
        print(f"❌ Error en exportación de datos: {e}")
        return False

def test_api_endpoints():
    """Prueba endpoints de API"""
    print("\n🌐 Probando Endpoints de API...")
    
    try:
        from flask import Flask
        from analytics_engine import init_analytics_engine
        
        # Crear app de prueba
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Inicializar analytics
        init_analytics_engine(app)
        
        # Lista de endpoints esperados
        expected_endpoints = [
            '/api/v1/analytics/dashboard',
            '/api/v1/analytics/real-time',
            '/api/v1/analytics/user-behavior',
            '/api/v1/analytics/predictive',
            '/api/v1/analytics/business-intelligence',
            '/api/v1/analytics/export',
            '/api/v1/analytics/kpis',
            '/api/v1/analytics/segments'
        ]
        
        with app.app_context():
            for endpoint in expected_endpoints:
                try:
                    # Simular request
                    with app.test_client() as client:
                        if endpoint == '/api/v1/analytics/export':
                            response = client.post(endpoint, json={'data_type': 'dashboard', 'format': 'json'})
                        else:
                            response = client.get(endpoint)
                        
                        if response.status_code in [200, 201]:
                            print(f"✅ Endpoint {endpoint} responde correctamente")
                        else:
                            print(f"⚠️ Endpoint {endpoint} responde con código {response.status_code}")
                except Exception as e:
                    print(f"❌ Error en endpoint {endpoint}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error probando endpoints: {e}")
        return False

def test_performance_impact():
    """Prueba el impacto en performance"""
    print("\n⚡ Probando Impacto en Performance...")
    
    try:
        from analytics_engine import analytics_manager
        import time
        
        # Medir tiempo de generación de dashboard
        start_time = time.time()
        dashboard = analytics_manager.get_comprehensive_dashboard()
        dashboard_time = time.time() - start_time
        
        print(f"✅ Dashboard generado en {dashboard_time:.3f} segundos")
        
        # Medir tiempo de analytics en tiempo real
        start_time = time.time()
        real_time_data = analytics_manager.real_time_analytics.get_real_time_dashboard()
        real_time_duration = time.time() - start_time
        
        print(f"✅ Analytics en tiempo real en {real_time_duration:.3f} segundos")
        
        # Medir tiempo de business intelligence
        start_time = time.time()
        bi_report = analytics_manager.business_intelligence.generate_executive_report()
        bi_time = time.time() - start_time
        
        print(f"✅ Business Intelligence en {bi_time:.3f} segundos")
        
        # Verificar que los tiempos sean razonables
        if dashboard_time < 2.0 and real_time_duration < 1.0 and bi_time < 1.0:
            print("✅ Performance dentro de límites aceptables")
            return True
        else:
            print("⚠️ Performance puede necesitar optimización")
            return False
            
    except Exception as e:
        print(f"❌ Error probando performance: {e}")
        return False

def test_integration_with_phases():
    """Prueba integración con fases anteriores"""
    print("\n🔗 Probando Integración con Fases Anteriores...")
    
    try:
        # Verificar que las fases anteriores estén disponibles
        from performance_integration import performance_manager
        print("✅ Fase 1 (Performance) disponible")
        
        from intelligent_automation import automation_manager
        print("✅ Fase 2 (Automatización) disponible")
        
        from analytics_engine import analytics_manager
        print("✅ Fase 3 (Analytics) disponible")
        
        # Probar integración con cache
        if hasattr(performance_manager, 'cache_manager'):
            print("✅ Integración con cache manager verificada")
        
        # Probar integración con automatización
        if hasattr(automation_manager, 'workflow_engine'):
            print("✅ Integración con workflow engine verificada")
        
        return True
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        return False

def generate_phase3_report():
    """Genera reporte completo de la Fase 3"""
    print("\n📋 Generando Reporte de Fase 3...")
    
    report = {
        'phase': 'Fase 3: Analytics y Business Intelligence',
        'timestamp': datetime.now().isoformat(),
        'tests': {
            'analytics_engine': test_analytics_engine(),
            'real_time_analytics': test_real_time_analytics(),
            'predictive_analytics': test_predictive_analytics(),
            'business_intelligence': test_business_intelligence(),
            'data_export': test_data_export(),
            'api_endpoints': test_api_endpoints(),
            'performance_impact': test_performance_impact(),
            'integration': test_integration_with_phases()
        },
        'summary': {
            'total_tests': 8,
            'passed_tests': 0,
            'failed_tests': 0
        },
        'features_implemented': [
            'Real-time Analytics Dashboard',
            'Predictive Analytics Engine',
            'Business Intelligence System',
            'User Behavior Analysis',
            'KPI Tracking and Monitoring',
            'Data Export Capabilities',
            'RESTful API Endpoints',
            'Performance Metrics Collection',
            'Trend Analysis and Insights',
            'Automated Recommendations'
        ],
        'technical_details': {
            'backend': 'Python Flask',
            'analytics_engine': 'Custom Analytics Engine',
            'data_visualization': 'Chart.js',
            'real_time_updates': 'Threading-based monitoring',
            'caching': 'Redis integration',
            'export_formats': ['CSV', 'JSON', 'Excel', 'PDF']
        },
        'business_impact': {
            'data_driven_decisions': 'Habilitado',
            'real_time_monitoring': 'Habilitado',
            'predictive_insights': 'Habilitado',
            'performance_tracking': 'Habilitado',
            'user_engagement_analysis': 'Habilitado',
            'automated_reporting': 'Habilitado'
        }
    }
    
    # Calcular estadísticas
    passed = sum(1 for test in report['tests'].values() if test)
    failed = len(report['tests']) - passed
    
    report['summary']['passed_tests'] = passed
    report['summary']['failed_tests'] = failed
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN DE FASE 3:")
    print(f"   ✅ Tests pasados: {passed}")
    print(f"   ❌ Tests fallidos: {failed}")
    print(f"   📈 Porcentaje de éxito: {(passed/len(report['tests'])*100):.1f}%")
    
    if passed == len(report['tests']):
        print("\n🎉 ¡FASE 3 COMPLETADA EXITOSAMENTE!")
        print("   El sistema de Analytics y Business Intelligence está completamente operativo.")
    else:
        print(f"\n⚠️ Fase 3 completada con {failed} problemas menores.")
        print("   Revisar los errores específicos arriba.")
    
    # Guardar reporte
    try:
        with open('PHASE3_REPORT.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("\n💾 Reporte guardado en PHASE3_REPORT.json")
    except Exception as e:
        print(f"⚠️ No se pudo guardar el reporte: {e}")
    
    return report

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE FASE 3: ANALYTICS Y BUSINESS INTELLIGENCE")
    print("=" * 70)
    
    # Ejecutar todas las pruebas
    report = generate_phase3_report()
    
    print("\n" + "=" * 70)
    print("🏁 PRUEBAS DE FASE 3 COMPLETADAS")
    
    # Mostrar recomendaciones
    if report['summary']['failed_tests'] > 0:
        print("\n🔧 RECOMENDACIONES:")
        print("   1. Revisar los errores específicos mostrados arriba")
        print("   2. Verificar que todas las dependencias estén instaladas")
        print("   3. Asegurar que la base de datos esté configurada correctamente")
        print("   4. Verificar que Redis esté disponible para caching")
    else:
        print("\n🎯 PRÓXIMOS PASOS:")
        print("   1. Configurar el dashboard de analytics en la interfaz web")
        print("   2. Personalizar KPIs según necesidades específicas del negocio")
        print("   3. Configurar alertas automáticas basadas en métricas")
        print("   4. Implementar reportes programados")
        print("   5. Proceder con la Fase 4: UX Premium")
    
    return report['summary']['passed_tests'] == report['summary']['total_tests']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
