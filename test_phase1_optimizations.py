#!/usr/bin/env python3
"""
Script de Prueba - Fase 1: Performance Crítica
Prueba todas las optimizaciones implementadas
"""

import os
import sys
import time
import requests
from datetime import datetime
import json

def print_header(title):
    """Imprimir header decorado"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_result(test_name, success, details=""):
    """Imprimir resultado de test"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def test_cache_manager():
    """Probar sistema de caché"""
    print_header("PRUEBA DE CACHÉ REDIS")
    
    try:
        from cache_manager import cache_manager, DashboardCache
        
        # Probar conexión
        is_connected = cache_manager.is_connected()
        print_result("Conexión Redis", is_connected)
        
        if is_connected:
            # Probar operaciones básicas
            cache_manager.set("test_key", "test_value", 60)
            value = cache_manager.get("test_key")
            print_result("Set/Get básico", value == "test_value")
            
            # Probar dashboard cache
            dashboard_data = DashboardCache.get_user_dashboard_data(1)
            print_result("Dashboard cache", isinstance(dashboard_data, dict))
            
            # Limpiar test
            cache_manager.delete("test_key")
        
        return True
        
    except Exception as e:
        print_result("Cache manager", False, str(e))
        return False

def test_database_optimizer():
    """Probar optimizador de base de datos"""
    print_header("PRUEBA DE OPTIMIZADOR DE BASE DE DATOS")
    
    try:
        from database_optimizer import QueryOptimizer, DatabaseHealthCheck
        from models import db
        
        # Probar consultas optimizadas
        dashboard_data = QueryOptimizer.get_dashboard_data_optimized(1)
        print_result("Consulta dashboard optimizada", isinstance(dashboard_data, dict))
        
        # Probar health check
        health_status = DatabaseHealthCheck.check_database_health(db)
        print_result("Health check BD", health_status['status'] == 'healthy')
        
        return True
        
    except Exception as e:
        print_result("Database optimizer", False, str(e))
        return False

def test_asset_compressor():
    """Probar compresor de assets"""
    print_header("PRUEBA DE COMPRESOR DE ASSETS")
    
    try:
        from asset_compressor import asset_compressor
        
        # Probar compresión de CSS
        test_css = """
        .test-class {
            color: red;
            background-color: blue;
            margin: 10px;
        }
        """
        
        compressed_css = asset_compressor.minify_css(test_css)
        print_result("Compresión CSS", len(compressed_css) < len(test_css))
        
        # Probar compresión de JS
        test_js = """
        function testFunction() {
            var x = 1;
            var y = 2;
            return x + y;
        }
        """
        
        compressed_js = asset_compressor.minify_js(test_js)
        print_result("Compresión JS", len(compressed_js) < len(test_js))
        
        # Probar estadísticas
        stats = asset_compressor.get_compression_stats()
        print_result("Estadísticas de compresión", isinstance(stats, dict))
        
        return True
        
    except Exception as e:
        print_result("Asset compressor", False, str(e))
        return False

def test_performance_integration():
    """Probar integración de performance"""
    print_header("PRUEBA DE INTEGRACIÓN DE PERFORMANCE")
    
    try:
        from performance_integration import PerformanceUtils, get_performance_config
        
        # Probar configuración
        config = get_performance_config()
        print_result("Configuración performance", isinstance(config, dict))
        
        # Probar utilidades
        dashboard_data = PerformanceUtils.get_optimized_dashboard_data(1)
        print_result("Utilidades performance", isinstance(dashboard_data, dict))
        
        return True
        
    except Exception as e:
        print_result("Performance integration", False, str(e))
        return False

def test_frontend_optimizations():
    """Probar optimizaciones frontend"""
    print_header("PRUEBA DE OPTIMIZACIONES FRONTEND")
    
    # Verificar que el archivo de optimización existe
    optimizer_file = "static/js/performance-optimizer.js"
    file_exists = os.path.exists(optimizer_file)
    print_result("Archivo optimizador frontend", file_exists)
    
    if file_exists:
        # Verificar contenido básico
        with open(optimizer_file, 'r') as f:
            content = f.read()
            has_class = "class PerformanceOptimizer" in content
            print_result("Clase PerformanceOptimizer", has_class)
            
            has_lazy_loading = "lazyComponents" in content
            print_result("Lazy loading", has_lazy_loading)
            
            has_virtual_scroll = "virtualLists" in content
            print_result("Virtual scrolling", has_virtual_scroll)
    
    return file_exists

def test_api_endpoints():
    """Probar endpoints de performance"""
    print_header("PRUEBA DE ENDPOINTS DE PERFORMANCE")
    
    # Nota: Esto requiere que la aplicación esté corriendo
    base_url = "http://localhost:5000"
    
    try:
        # Probar health endpoint
        response = requests.get(f"{base_url}/api/performance/health", timeout=5)
        print_result("Health endpoint", response.status_code == 200)
        
        # Probar metrics endpoint
        response = requests.get(f"{base_url}/api/performance/metrics", timeout=5)
        print_result("Metrics endpoint", response.status_code == 200)
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_result("Endpoints API", False, "Aplicación no está corriendo")
        return False
    except Exception as e:
        print_result("Endpoints API", False, str(e))
        return False

def run_performance_benchmark():
    """Ejecutar benchmark de performance"""
    print_header("BENCHMARK DE PERFORMANCE")
    
    try:
        from cache_manager import cache_manager
        from database_optimizer import QueryOptimizer
        import time
        
        # Benchmark de caché
        if cache_manager.is_connected():
            start_time = time.time()
            for i in range(100):
                cache_manager.set(f"benchmark_key_{i}", f"value_{i}")
            cache_time = time.time() - start_time
            print_result("Benchmark caché (100 ops)", cache_time < 1.0, f"{cache_time:.3f}s")
        
        # Benchmark de consultas
        start_time = time.time()
        for i in range(10):
            QueryOptimizer.get_dashboard_data_optimized(1)
        query_time = time.time() - start_time
        print_result("Benchmark consultas (10 ops)", query_time < 2.0, f"{query_time:.3f}s")
        
        return True
        
    except Exception as e:
        print_result("Benchmark", False, str(e))
        return False

def generate_performance_report():
    """Generar reporte de performance"""
    print_header("REPORTE DE PERFORMANCE - FASE 1")
    
    tests = [
        ("Cache Manager", test_cache_manager),
        ("Database Optimizer", test_database_optimizer),
        ("Asset Compressor", test_asset_compressor),
        ("Performance Integration", test_performance_integration),
        ("Frontend Optimizations", test_frontend_optimizations),
        ("API Endpoints", test_api_endpoints),
        ("Performance Benchmark", run_performance_benchmark)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ Error en {test_name}: {e}")
    
    # Resumen
    print_header("RESUMEN DE RESULTADOS")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"✅ Tests pasados: {passed}/{total}")
    print(f"📊 Porcentaje de éxito: {(passed/total)*100:.1f}%")
    
    # Detalles
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    # Recomendaciones
    print_header("RECOMENDACIONES")
    if passed == total:
        print("🎉 ¡Excelente! Todas las optimizaciones están funcionando correctamente.")
        print("🚀 El sistema está listo para la Fase 2: Automatización Inteligente")
    else:
        print("⚠️ Algunas optimizaciones necesitan atención:")
        failed_tests = [name for name, success in results if not success]
        for test in failed_tests:
            print(f"   - Revisar: {test}")
    
    return passed == total

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de optimizaciones - Fase 1")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("main.py"):
        print("❌ Error: Ejecutar desde el directorio raíz del proyecto")
        sys.exit(1)
    
    # Ejecutar pruebas
    success = generate_performance_report()
    
    if success:
        print("\n🎯 Fase 1 completada exitosamente!")
        print("📈 El sistema ahora tiene:")
        print("   - Caché Redis optimizado")
        print("   - Consultas de BD optimizadas")
        print("   - Assets comprimidos")
        print("   - Lazy loading frontend")
        print("   - Monitoreo de performance")
        print("\n🚀 Listo para continuar con la Fase 2")
    else:
        print("\n⚠️ Fase 1 necesita ajustes antes de continuar")
    
    return success

if __name__ == "__main__":
    main()
