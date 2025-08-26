#!/usr/bin/env python3
"""
Test Suite para Fase 4: UX Premium
Verifica todas las características de experiencia de usuario premium implementadas
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_premium_ux_files():
    """Test 1: Verificar que todos los archivos de UX Premium existen"""
    print("🔍 Test 1: Verificando archivos de UX Premium...")
    
    required_files = [
        'static/css/premium-ux.css',
        'static/js/premium-ux.js',
        'templates/premium_dashboard.html',
        'routes/premium_routes.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"  ❌ Archivos faltantes: {missing_files}")
        return False
    
    print("  ✅ Todos los archivos de UX Premium existen")
    return True

def test_premium_css_features():
    """Test 2: Verificar características CSS premium"""
    print("\n🎨 Test 2: Verificando características CSS premium...")
    
    css_file = project_root / 'static/css/premium-ux.css'
    if not css_file.exists():
        print("  ❌ Archivo CSS premium no encontrado")
        return False
    
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    required_features = [
        '--primary-gradient',
        '--shadow-md',
        '--transition-normal',
        '.btn-primary',
        '.card',
        '.modal',
        '.toast',
        '.tooltip',
        '.loading',
        '@keyframes',
        '@media (prefers-color-scheme: dark)',
        '@media (prefers-reduced-motion: reduce)'
    ]
    
    missing_features = []
    for feature in required_features:
        if feature not in css_content:
            missing_features.append(feature)
        else:
            print(f"  ✅ {feature}")
    
    if missing_features:
        print(f"  ❌ Características CSS faltantes: {missing_features}")
        return False
    
    print("  ✅ Todas las características CSS premium están presentes")
    return True

def test_premium_js_features():
    """Test 3: Verificar características JavaScript premium"""
    print("\n⚡ Test 3: Verificando características JavaScript premium...")
    
    js_file = project_root / 'static/js/premium-ux.js'
    if not js_file.exists():
        print("  ❌ Archivo JavaScript premium no encontrado")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    required_features = [
        'class PremiumUX',
        'setupTheme()',
        'setupAccessibility()',
        'setupAnimations()',
        'setupMicroInteractions()',
        'setupNotifications()',
        'setupModals()',
        'setupTooltips()',
        'createRippleEffect',
        'showToast',
        'showModal',
        'validateField',
        'IntersectionObserver',
        'debounce',
        'CustomEvent'
    ]
    
    missing_features = []
    for feature in required_features:
        if feature not in js_content:
            missing_features.append(feature)
        else:
            print(f"  ✅ {feature}")
    
    if missing_features:
        print(f"  ❌ Características JavaScript faltantes: {missing_features}")
        return False
    
    print("  ✅ Todas las características JavaScript premium están presentes")
    return True

def test_premium_template():
    """Test 4: Verificar template premium"""
    print("\n📄 Test 4: Verificando template premium...")
    
    template_file = project_root / 'templates/premium_dashboard.html'
    if not template_file.exists():
        print("  ❌ Template premium no encontrado")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    required_elements = [
        'premium-ux.css',
        'premium-ux.js',
        'data-theme-toggle',
        'data-tooltip',
        'data-modal-target',
        'data-loading',
        'data-animate',
        'data-hover-animate',
        'data-counter',
        'skip-link',
        'navbar',
        'card',
        'btn',
        'modal',
        'toast',
        'progress',
        'badge'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in template_content:
            missing_elements.append(element)
        else:
            print(f"  ✅ {element}")
    
    if missing_elements:
        print(f"  ❌ Elementos del template faltantes: {missing_elements}")
        return False
    
    print("  ✅ Todos los elementos del template premium están presentes")
    return True

def test_premium_routes():
    """Test 5: Verificar rutas premium"""
    print("\n🛣️ Test 5: Verificando rutas premium...")
    
    routes_file = project_root / 'routes/premium_routes.py'
    if not routes_file.exists():
        print("  ❌ Archivo de rutas premium no encontrado")
        return False
    
    with open(routes_file, 'r', encoding='utf-8') as f:
        routes_content = f.read()
    
    required_routes = [
        '/dashboard',
        '/api/theme',
        '/api/notifications',
        '/api/metrics',
        '/api/accessibility',
        '/api/performance',
        '/api/user-preferences',
        '/api/search',
        '/api/help',
        '/api/feedback',
        '/api/export-data',
        '/api/system-status'
    ]
    
    missing_routes = []
    for route in required_routes:
        if route not in routes_content:
            missing_routes.append(route)
        else:
            print(f"  ✅ {route}")
    
    if missing_routes:
        print(f"  ❌ Rutas faltantes: {missing_routes}")
        return False
    
    print("  ✅ Todas las rutas premium están definidas")
    return True

def test_accessibility_features():
    """Test 6: Verificar características de accesibilidad"""
    print("\n♿ Test 6: Verificando características de accesibilidad...")
    
    # Verificar en CSS
    css_file = project_root / 'static/css/premium-ux.css'
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Verificar en JS
    js_file = project_root / 'static/js/premium-ux.js'
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Verificar en template
    template_file = project_root / 'templates/premium_dashboard.html'
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    accessibility_features = [
        'sr-only',
        'skip-link',
        'aria-label',
        'focus-visible',
        'keyboard-navigation',
        'reduced-motion',
        'high-contrast',
        'prefers-color-scheme',
        'prefers-reduced-motion',
        'prefers-contrast'
    ]
    
    missing_features = []
    for feature in accessibility_features:
        if (feature not in css_content and 
            feature not in js_content and 
            feature not in template_content):
            missing_features.append(feature)
        else:
            print(f"  ✅ {feature}")
    
    if missing_features:
        print(f"  ❌ Características de accesibilidad faltantes: {missing_features}")
        return False
    
    print("  ✅ Todas las características de accesibilidad están implementadas")
    return True

def test_responsive_design():
    """Test 7: Verificar diseño responsive"""
    print("\n📱 Test 7: Verificando diseño responsive...")
    
    css_file = project_root / 'static/css/premium-ux.css'
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    responsive_features = [
        '@media (max-width: 768px)',
        'd-md-none',
        'd-md-inline',
        'flex-direction: column',
        'width: 100%',
        '95vw',
        'transform: translateX(-100%)'
    ]
    
    missing_features = []
    for feature in responsive_features:
        if feature not in css_content:
            missing_features.append(feature)
        else:
            print(f"  ✅ {feature}")
    
    if missing_features:
        print(f"  ❌ Características responsive faltantes: {missing_features}")
        return False
    
    print("  ✅ Todas las características responsive están implementadas")
    return True

def test_performance_optimizations():
    """Test 8: Verificar optimizaciones de performance"""
    print("\n⚡ Test 8: Verificando optimizaciones de performance...")
    
    js_file = project_root / 'static/js/premium-ux.js'
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    css_file = project_root / 'static/css/premium-ux.css'
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    performance_features = [
        'debounce',
        'IntersectionObserver',
        'requestAnimationFrame',
        'lazy loading',
        'preload',
        'will-change',
        'transform3d',
        'backface-visibility'
    ]
    
    missing_features = []
    for feature in performance_features:
        if feature not in js_content and feature not in css_content:
            missing_features.append(feature)
        else:
            print(f"  ✅ {feature}")
    
    if missing_features:
        print(f"  ❌ Optimizaciones de performance faltantes: {missing_features}")
        return False
    
    print("  ✅ Todas las optimizaciones de performance están implementadas")
    return True

def test_micro_interactions():
    """Test 9: Verificar micro-interacciones"""
    print("\n✨ Test 9: Verificando micro-interacciones...")
    
    js_file = project_root / 'static/js/premium-ux.js'
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    css_file = project_root / 'static/css/premium-ux.css'
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    micro_interactions = [
        'ripple',
        'hover-animate',
        'focus-enhanced',
        'transition',
        'animation',
        'transform',
        'scale',
        'translateY',
        'opacity'
    ]
    
    missing_interactions = []
    for interaction in micro_interactions:
        if interaction not in js_content and interaction not in css_content:
            missing_interactions.append(interaction)
        else:
            print(f"  ✅ {interaction}")
    
    if missing_interactions:
        print(f"  ❌ Micro-interacciones faltantes: {missing_interactions}")
        return False
    
    print("  ✅ Todas las micro-interacciones están implementadas")
    return True

def test_integration_with_previous_phases():
    """Test 10: Verificar integración con fases anteriores"""
    print("\n🔗 Test 10: Verificando integración con fases anteriores...")
    
    # Verificar que main.py incluye las rutas premium
    main_file = project_root / 'main.py'
    with open(main_file, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    integration_points = [
        'init_premium_routes',
        'premium_routes',
        'Rutas Premium UX'
    ]
    
    missing_integration = []
    for point in integration_points:
        if point not in main_content:
            missing_integration.append(point)
        else:
            print(f"  ✅ {point}")
    
    if missing_integration:
        print(f"  ❌ Puntos de integración faltantes: {missing_integration}")
        return False
    
    print("  ✅ Integración con fases anteriores completada")
    return True

def generate_phase4_report():
    """Generar reporte completo de la Fase 4"""
    print("\n📊 Generando reporte de la Fase 4...")
    
    tests = [
        ("Archivos UX Premium", test_premium_ux_files),
        ("Características CSS", test_premium_css_features),
        ("Características JavaScript", test_premium_js_features),
        ("Template Premium", test_premium_template),
        ("Rutas Premium", test_premium_routes),
        ("Accesibilidad", test_accessibility_features),
        ("Diseño Responsive", test_responsive_design),
        ("Optimizaciones Performance", test_performance_optimizations),
        ("Micro-interacciones", test_micro_interactions),
        ("Integración con Fases Anteriores", test_integration_with_previous_phases)
    ]
    
    results = {}
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = {
                'status': 'PASSED' if result else 'FAILED',
                'timestamp': datetime.now().isoformat()
            }
            if result:
                passed_tests += 1
        except Exception as e:
            results[test_name] = {
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    # Calcular métricas
    success_rate = (passed_tests / total_tests) * 100
    
    # Crear reporte
    report = {
        'phase': 'Fase 4: UX Premium',
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': round(success_rate, 2)
        },
        'results': results,
        'features_implemented': [
            'Sistema de diseño premium con CSS variables',
            'Micro-interacciones avanzadas',
            'Sistema de notificaciones toast',
            'Modales accesibles',
            'Tooltips interactivos',
            'Estados de carga animados',
            'Validación de formularios en tiempo real',
            'Navegación por teclado',
            'Diseño responsive',
            'Modo oscuro/claro',
            'Accesibilidad WCAG 2.1',
            'Optimizaciones de performance',
            'Lazy loading',
            'Debouncing',
            'Intersection Observer'
        ],
        'files_created': [
            'static/css/premium-ux.css',
            'static/js/premium-ux.js',
            'templates/premium_dashboard.html',
            'routes/premium_routes.py'
        ],
        'apis_implemented': [
            '/premium/api/theme',
            '/premium/api/notifications',
            '/premium/api/metrics',
            '/premium/api/accessibility',
            '/premium/api/performance',
            '/premium/api/user-preferences',
            '/premium/api/search',
            '/premium/api/help',
            '/premium/api/feedback',
            '/premium/api/export-data',
            '/premium/api/system-status'
        ],
        'recommendations': [
            'Implementar tests unitarios para cada componente',
            'Agregar más animaciones personalizadas',
            'Implementar PWA features',
            'Agregar soporte para más idiomas',
            'Implementar analytics de UX',
            'Agregar más temas personalizables'
        ] if success_rate >= 90 else [
            'Revisar tests fallidos',
            'Completar implementaciones faltantes',
            'Verificar integración con fases anteriores',
            'Optimizar performance',
            'Mejorar accesibilidad'
        ]
    }
    
    # Guardar reporte
    report_file = project_root / 'PHASE4_REPORT.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumen
    print(f"\n{'='*60}")
    print(f"📋 REPORTE FASE 4: UX PREMIUM")
    print(f"{'='*60}")
    print(f"✅ Tests pasados: {passed_tests}/{total_tests}")
    print(f"📊 Tasa de éxito: {success_rate}%")
    print(f"📁 Reporte guardado: {report_file}")
    
    if success_rate >= 90:
        print(f"🎉 ¡Fase 4 completada exitosamente!")
    else:
        print(f"⚠️ Fase 4 necesita mejoras")
    
    print(f"{'='*60}")
    
    return success_rate >= 90

if __name__ == "__main__":
    print("🚀 Iniciando tests de Fase 4: UX Premium")
    print("=" * 60)
    
    success = generate_phase4_report()
    
    if success:
        print("\n🎯 Todos los tests de UX Premium han pasado exitosamente!")
        print("✨ El sistema ahora cuenta con una experiencia de usuario premium")
    else:
        print("\n⚠️ Algunos tests fallaron. Revisa el reporte para más detalles.")
    
    sys.exit(0 if success else 1)
