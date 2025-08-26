"""
Manejo de dependencias opcionales para las fases 1-6
Evita errores cuando las dependencias no están instaladas
"""

import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Variables para almacenar módulos importados
_optional_modules = {}

def safe_import(module_name: str, package_name: str = None) -> Optional[Any]:
    """
    Importar módulo de forma segura, retorna None si no está disponible
    
    Args:
        module_name: Nombre del módulo a importar
        package_name: Nombre del paquete (opcional)
    
    Returns:
        Módulo importado o None si no está disponible
    """
    if module_name in _optional_modules:
        return _optional_modules[module_name]
    
    try:
        if package_name:
            module = __import__(package_name, fromlist=[module_name])
        else:
            module = __import__(module_name)
        
        _optional_modules[module_name] = module
        logger.info(f"✅ {module_name} importado correctamente")
        return module
    except ImportError as e:
        logger.warning(f"⚠️ {module_name} no disponible: {e}")
        _optional_modules[module_name] = None
        return None
    except Exception as e:
        logger.error(f"❌ Error importando {module_name}: {e}")
        _optional_modules[module_name] = None
        return None

# Importaciones seguras de dependencias opcionales
NUMPY_AVAILABLE = safe_import('numpy') is not None
PANDAS_AVAILABLE = safe_import('pandas') is not None
MATPLOTLIB_AVAILABLE = safe_import('matplotlib') is not None
SEABORN_AVAILABLE = safe_import('seaborn') is not None
SKLEARN_AVAILABLE = safe_import('sklearn') is not None
GOOGLEMAPS_AVAILABLE = safe_import('googlemaps') is not None
DOCKER_AVAILABLE = safe_import('docker') is not None
BOTO3_AVAILABLE = safe_import('boto3') is not None
SENDGRID_AVAILABLE = safe_import('sendgrid') is not None
STRIPE_AVAILABLE = safe_import('stripe') is not None
PAYPAL_AVAILABLE = safe_import('paypalrestsdk') is not None
OPENWEATHERMAP_AVAILABLE = safe_import('openweathermap') is not None
GEOPY_AVAILABLE = safe_import('geopy') is not None

# Funciones de conveniencia para obtener módulos
def get_numpy():
    """Obtener numpy si está disponible"""
    return safe_import('numpy')

def get_pandas():
    """Obtener pandas si está disponible"""
    return safe_import('pandas')

def get_matplotlib():
    """Obtener matplotlib si está disponible"""
    return safe_import('matplotlib')

def get_seaborn():
    """Obtener seaborn si está disponible"""
    return safe_import('seaborn')

def get_sklearn():
    """Obtener scikit-learn si está disponible"""
    return safe_import('sklearn')

def get_googlemaps():
    """Obtener googlemaps si está disponible"""
    return safe_import('googlemaps')

def get_docker():
    """Obtener docker si está disponible"""
    return safe_import('docker')

def get_boto3():
    """Obtener boto3 si está disponible"""
    return safe_import('boto3')

def get_sendgrid():
    """Obtener sendgrid si está disponible"""
    return safe_import('sendgrid')

def get_stripe():
    """Obtener stripe si está disponible"""
    return safe_import('stripe')

def get_paypal():
    """Obtener paypalrestsdk si está disponible"""
    return safe_import('paypalrestsdk')

def get_openweathermap():
    """Obtener openweathermap si está disponible"""
    return safe_import('openweathermap')

def get_geopy():
    """Obtener geopy si está disponible"""
    return safe_import('geopy')

# Función para verificar dependencias requeridas
def check_required_dependencies(required_modules: list) -> dict:
    """
    Verificar si las dependencias requeridas están disponibles
    
    Args:
        required_modules: Lista de nombres de módulos requeridos
    
    Returns:
        Dict con el estado de cada módulo
    """
    status = {}
    for module in required_modules:
        status[module] = safe_import(module) is not None
    return status

# Función para mostrar estado de dependencias
def show_dependencies_status():
    """Mostrar el estado de todas las dependencias opcionales"""
    dependencies = {
        'numpy': NUMPY_AVAILABLE,
        'pandas': PANDAS_AVAILABLE,
        'matplotlib': MATPLOTLIB_AVAILABLE,
        'seaborn': SEABORN_AVAILABLE,
        'scikit-learn': SKLEARN_AVAILABLE,
        'googlemaps': GOOGLEMAPS_AVAILABLE,
        'docker': DOCKER_AVAILABLE,
        'boto3': BOTO3_AVAILABLE,
        'sendgrid': SENDGRID_AVAILABLE,
        'stripe': STRIPE_AVAILABLE,
        'paypalrestsdk': PAYPAL_AVAILABLE,
        'openweathermap': OPENWEATHERMAP_AVAILABLE,
        'geopy': GEOPY_AVAILABLE
    }
    
    logger.info("📦 Estado de dependencias opcionales:")
    for dep, available in dependencies.items():
        status = "✅" if available else "❌"
        logger.info(f"  {status} {dep}")
    
    return dependencies
