#!/usr/bin/env python3
"""
Script de prueba para verificar el monitoreo de seguridad
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_security_monitoring():
    """Probar el monitoreo de seguridad"""
    try:
        # Importar el sistema de monitoreo
        from intelligent_monitoring import IntelligentMonitoringSystem
        
        # Crear instancia del sistema
        monitoring_system = IntelligentMonitoringSystem()
        
        # Probar las funciones de seguridad
        logger.info("Probando _get_recent_security_events()...")
        security_events = monitoring_system._get_recent_security_events()
        logger.info(f"Eventos de seguridad obtenidos: {len(security_events)}")
        
        logger.info("Probando _get_failed_login_attempts()...")
        failed_logins = monitoring_system._get_failed_login_attempts()
        logger.info(f"Intentos de login fallidos obtenidos: {len(failed_logins)}")
        
        logger.info("Probando _get_suspicious_activities()...")
        suspicious_activities = monitoring_system._get_suspicious_activities()
        logger.info(f"Actividades sospechosas obtenidas: {len(suspicious_activities)}")
        
        # Probar el monitoreo completo
        logger.info("Probando monitoreo de seguridad completo...")
        try:
            # Simular una ejecución del monitoreo
            security_events = monitoring_system._get_recent_security_events()
            failed_logins = monitoring_system._get_failed_login_attempts()
            suspicious_activities = monitoring_system._get_suspicious_activities()
            
            # Validar que las funciones retornen listas válidas
            if security_events is None:
                security_events = []
            if failed_logins is None:
                failed_logins = []
            if suspicious_activities is None:
                suspicious_activities = []
            
            # Probar len() en todas las listas
            logger.info(f"Longitud de security_events: {len(security_events)}")
            logger.info(f"Longitud de failed_logins: {len(failed_logins)}")
            logger.info(f"Longitud de suspicious_activities: {len(suspicious_activities)}")
            
            logger.info("✅ Todas las pruebas pasaron exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en el monitoreo de seguridad: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error importando o inicializando el sistema: {e}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando pruebas del monitoreo de seguridad...")
    success = test_security_monitoring()
    
    if success:
        logger.info("🎉 Todas las pruebas completadas exitosamente")
        sys.exit(0)
    else:
        logger.error("💥 Algunas pruebas fallaron")
        sys.exit(1)
