"""
Sistema de Backup Automatizado
Proporciona respaldos programados y recuperación de datos
"""

import os
import shutil
import sqlite3
import zipfile
import json
import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from flask import current_app
from models import db
import subprocess
import hashlib
from typing import Dict, List, Optional

class BackupService:
    """Servicio de backup automatizado"""
    
    def __init__(self, app=None):
        self.app = app
        self.backup_dir = None
        self.scheduler_thread = None
        self.is_running = False
        self.backup_history = []
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar servicio con la aplicación"""
        self.app = app
        
        # Configurar directorio de backups
        self.backup_dir = Path(app.config.get('BACKUP_DIR', 'backups'))
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configurar programación de backups
        self.setup_backup_schedule()
        
        # Iniciar scheduler en background
        self.start_scheduler()
        
        print("✅ Servicio de backup inicializado")
    
    def setup_backup_schedule(self):
        """Configurar programación de backups"""
        # Backup diario a las 2:00 AM
        schedule.every().day.at("02:00").do(self.create_full_backup)
        
        # Backup incremental cada 6 horas
        schedule.every(6).hours.do(self.create_incremental_backup)
        
        # Backup de configuración cada hora
        schedule.every().hour.do(self.backup_configuration)
        
        # Limpieza de backups antiguos cada domingo
        schedule.every().sunday.at("03:00").do(self.cleanup_old_backups)
        
        print("✅ Programación de backups configurada")
    
    def start_scheduler(self):
        """Iniciar scheduler en background"""
        if not self.is_running:
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            print("✅ Scheduler de backups iniciado")
    
    def stop_scheduler(self):
        """Detener scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        print("✅ Scheduler de backups detenido")
    
    def _run_scheduler(self):
        """Ejecutar scheduler en loop"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
    
    def create_full_backup(self) -> Dict:
        """Crear backup completo del sistema"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"full_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            print(f"🔄 Iniciando backup completo: {backup_name}")
            
            backup_info = {
                'type': 'full',
                'timestamp': timestamp,
                'name': backup_name,
                'path': str(backup_path),
                'status': 'in_progress',
                'files': [],
                'size': 0,
                'checksum': None
            }
            
            # 1. Backup de base de datos
            db_backup = self._backup_database(backup_path)
            backup_info['files'].append(db_backup)
            
            # 2. Backup de archivos de configuración
            config_backup = self._backup_configuration(backup_path)
            backup_info['files'].extend(config_backup)
            
            # 3. Backup de archivos estáticos
            static_backup = self._backup_static_files(backup_path)
            backup_info['files'].extend(static_backup)
            
            # 4. Backup de logs
            logs_backup = self._backup_logs(backup_path)
            backup_info['files'].extend(logs_backup)
            
            # 5. Backup de uploads/media
            media_backup = self._backup_media_files(backup_path)
            backup_info['files'].extend(media_backup)
            
            # 6. Crear archivo comprimido
            zip_path = self._create_compressed_backup(backup_path)
            
            # 7. Calcular checksum
            backup_info['checksum'] = self._calculate_checksum(zip_path)
            backup_info['size'] = os.path.getsize(zip_path)
            backup_info['compressed_path'] = str(zip_path)
            
            # 8. Limpiar directorio temporal
            shutil.rmtree(backup_path)
            
            backup_info['status'] = 'completed'
            backup_info['duration'] = self._get_duration(timestamp)
            
            # Registrar backup
            self.backup_history.append(backup_info)
            self._save_backup_metadata(backup_info)
            
            print(f"✅ Backup completo finalizado: {backup_name}")
            print(f"   Tamaño: {backup_info['size'] / 1024 / 1024:.2f} MB")
            print(f"   Archivos: {len(backup_info['files'])}")
            
            return backup_info
            
        except Exception as e:
            backup_info['status'] = 'failed'
            backup_info['error'] = str(e)
            current_app.logger.error(f"Error en backup completo: {str(e)}")
            return backup_info
    
    def create_incremental_backup(self) -> Dict:
        """Crear backup incremental"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"incremental_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            print(f"🔄 Iniciando backup incremental: {backup_name}")
            
            backup_info = {
                'type': 'incremental',
                'timestamp': timestamp,
                'name': backup_name,
                'path': str(backup_path),
                'status': 'in_progress',
                'files': [],
                'size': 0,
                'checksum': None
            }
            
            # Obtener último backup para comparar
            last_backup_time = self._get_last_backup_time()
            
            # Solo respaldar archivos modificados desde el último backup
            modified_files = self._get_modified_files(last_backup_time)
            
            if not modified_files:
                print("ℹ️ No hay archivos modificados para backup incremental")
                backup_info['status'] = 'skipped'
                return backup_info
            
            # Backup de archivos modificados
            for file_path in modified_files:
                try:
                    relative_path = os.path.relpath(file_path)
                    backup_file_path = backup_path / relative_path
                    backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_file_path)
                    backup_info['files'].append(relative_path)
                except Exception as e:
                    print(f"⚠️ Error copiando {file_path}: {str(e)}")
            
            # Crear archivo comprimido
            zip_path = self._create_compressed_backup(backup_path)
            
            # Calcular checksum y tamaño
            backup_info['checksum'] = self._calculate_checksum(zip_path)
            backup_info['size'] = os.path.getsize(zip_path)
            backup_info['compressed_path'] = str(zip_path)
            
            # Limpiar directorio temporal
            shutil.rmtree(backup_path)
            
            backup_info['status'] = 'completed'
            backup_info['duration'] = self._get_duration(timestamp)
            
            # Registrar backup
            self.backup_history.append(backup_info)
            self._save_backup_metadata(backup_info)
            
            print(f"✅ Backup incremental finalizado: {backup_name}")
            print(f"   Archivos modificados: {len(backup_info['files'])}")
            
            return backup_info
            
        except Exception as e:
            backup_info['status'] = 'failed'
            backup_info['error'] = str(e)
            current_app.logger.error(f"Error en backup incremental: {str(e)}")
            return backup_info
    
    def backup_configuration(self) -> Dict:
        """Backup solo de configuración"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"config_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            backup_info = {
                'type': 'configuration',
                'timestamp': timestamp,
                'name': backup_name,
                'status': 'in_progress',
                'files': []
            }
            
            # Backup de archivos de configuración
            config_files = self._backup_configuration(backup_path)
            backup_info['files'].extend(config_files)
            
            # Crear archivo comprimido
            zip_path = self._create_compressed_backup(backup_path)
            backup_info['compressed_path'] = str(zip_path)
            backup_info['size'] = os.path.getsize(zip_path)
            
            # Limpiar directorio temporal
            shutil.rmtree(backup_path)
            
            backup_info['status'] = 'completed'
            
            print(f"✅ Backup de configuración completado: {backup_name}")
            
            return backup_info
            
        except Exception as e:
            backup_info['status'] = 'failed'
            backup_info['error'] = str(e)
            current_app.logger.error(f"Error en backup de configuración: {str(e)}")
            return backup_info
    
    def _backup_database(self, backup_path: Path) -> str:
        """Backup de la base de datos"""
        try:
            db_file = "instance/database.db"  # Ajustar según configuración
            if os.path.exists(db_file):
                backup_db_path = backup_path / "database.db"
                
                # Usar VACUUM INTO para SQLite (crea copia compacta)
                conn = sqlite3.connect(db_file)
                conn.execute(f"VACUUM INTO '{backup_db_path}'")
                conn.close()
                
                print(f"✅ Base de datos respaldada: {backup_db_path}")
                return "database.db"
            else:
                print("⚠️ Archivo de base de datos no encontrado")
                return None
                
        except Exception as e:
            print(f"❌ Error respaldando base de datos: {str(e)}")
            return None
    
    def _backup_configuration(self, backup_path: Path) -> List[str]:
        """Backup de archivos de configuración"""
        config_files = [
            "config.py",
            "app.py", 
            "models.py",
            "requirements.txt",
            ".env",
            ".flaskenv"
        ]
        
        backed_up = []
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    shutil.copy2(config_file, backup_path / config_file)
                    backed_up.append(config_file)
                    print(f"✅ Configuración respaldada: {config_file}")
                except Exception as e:
                    print(f"⚠️ Error respaldando {config_file}: {str(e)}")
        
        return backed_up
    
    def _backup_static_files(self, backup_path: Path) -> List[str]:
        """Backup de archivos estáticos"""
        static_dirs = ["static", "templates"]
        backed_up = []
        
        for static_dir in static_dirs:
            if os.path.exists(static_dir):
                try:
                    backup_static_path = backup_path / static_dir
                    shutil.copytree(static_dir, backup_static_path)
                    backed_up.append(static_dir)
                    print(f"✅ Directorio estático respaldado: {static_dir}")
                except Exception as e:
                    print(f"⚠️ Error respaldando {static_dir}: {str(e)}")
        
        return backed_up
    
    def _backup_logs(self, backup_path: Path) -> List[str]:
        """Backup de logs"""
        logs_dir = "logs"
        if os.path.exists(logs_dir):
            try:
                backup_logs_path = backup_path / logs_dir
                shutil.copytree(logs_dir, backup_logs_path)
                print(f"✅ Logs respaldados: {logs_dir}")
                return [logs_dir]
            except Exception as e:
                print(f"⚠️ Error respaldando logs: {str(e)}")
        
        return []
    
    def _backup_media_files(self, backup_path: Path) -> List[str]:
        """Backup de archivos multimedia/uploads"""
        media_dirs = ["uploads", "media", "files"]
        backed_up = []
        
        for media_dir in media_dirs:
            if os.path.exists(media_dir):
                try:
                    backup_media_path = backup_path / media_dir
                    shutil.copytree(media_dir, backup_media_path)
                    backed_up.append(media_dir)
                    print(f"✅ Media respaldado: {media_dir}")
                except Exception as e:
                    print(f"⚠️ Error respaldando {media_dir}: {str(e)}")
        
        return backed_up
    
    def _create_compressed_backup(self, backup_path: Path) -> Path:
        """Crear archivo comprimido del backup"""
        zip_path = backup_path.with_suffix('.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Backup comprimido creado: {zip_path}")
        return zip_path
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcular checksum MD5 del archivo"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_duration(self, start_timestamp: str) -> float:
        """Calcular duración del backup"""
        start_time = datetime.strptime(start_timestamp, "%Y%m%d_%H%M%S")
        end_time = datetime.now()
        return (end_time - start_time).total_seconds()
    
    def _get_last_backup_time(self) -> datetime:
        """Obtener timestamp del último backup"""
        if self.backup_history:
            last_backup = max(self.backup_history, key=lambda x: x['timestamp'])
            return datetime.strptime(last_backup['timestamp'], "%Y%m%d_%H%M%S")
        else:
            # Si no hay backups previos, usar hace 24 horas
            return datetime.now() - timedelta(days=1)
    
    def _get_modified_files(self, since: datetime) -> List[str]:
        """Obtener archivos modificados desde una fecha"""
        modified_files = []
        
        # Directorios a verificar
        check_dirs = [".", "app", "static", "templates", "instance"]
        
        for check_dir in check_dirs:
            if os.path.exists(check_dir):
                for root, dirs, files in os.walk(check_dir):
                    # Excluir directorios de backup y cache
                    dirs[:] = [d for d in dirs if d not in ['backups', '__pycache__', '.git']]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                            if mtime > since:
                                modified_files.append(file_path)
                        except Exception:
                            continue
        
        return modified_files
    
    def _save_backup_metadata(self, backup_info: Dict):
        """Guardar metadata del backup"""
        metadata_file = self.backup_dir / "backup_metadata.json"
        
        try:
            # Cargar metadata existente
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {'backups': []}
            
            # Agregar nuevo backup
            metadata['backups'].append(backup_info)
            
            # Guardar metadata actualizada
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
                
        except Exception as e:
            print(f"⚠️ Error guardando metadata: {str(e)}")
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Limpiar backups antiguos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            deleted_count = 0
            
            for backup_file in self.backup_dir.glob("*.zip"):
                try:
                    # Extraer timestamp del nombre del archivo
                    timestamp_str = backup_file.stem.split('_')[-2] + '_' + backup_file.stem.split('_')[-1]
                    backup_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    if backup_date < cutoff_date:
                        backup_file.unlink()
                        deleted_count += 1
                        print(f"🗑️ Backup eliminado: {backup_file.name}")
                        
                except Exception as e:
                    print(f"⚠️ Error procesando {backup_file}: {str(e)}")
            
            print(f"✅ Limpieza completada: {deleted_count} backups eliminados")
            
        except Exception as e:
            current_app.logger.error(f"Error en limpieza de backups: {str(e)}")
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restaurar desde un backup"""
        try:
            backup_file = self.backup_dir / f"{backup_name}.zip"
            
            if not backup_file.exists():
                print(f"❌ Backup no encontrado: {backup_name}")
                return False
            
            print(f"🔄 Iniciando restauración desde: {backup_name}")
            
            # Crear directorio temporal para extracción
            temp_dir = self.backup_dir / f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(exist_ok=True)
            
            # Extraer backup
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Restaurar base de datos
            db_backup = temp_dir / "database.db"
            if db_backup.exists():
                shutil.copy2(db_backup, "instance/database.db")
                print("✅ Base de datos restaurada")
            
            # Restaurar archivos de configuración
            config_files = ["config.py", "app.py", "models.py"]
            for config_file in config_files:
                config_backup = temp_dir / config_file
                if config_backup.exists():
                    shutil.copy2(config_backup, config_file)
                    print(f"✅ Configuración restaurada: {config_file}")
            
            # Restaurar directorios estáticos
            static_dirs = ["static", "templates"]
            for static_dir in static_dirs:
                static_backup = temp_dir / static_dir
                if static_backup.exists():
                    if os.path.exists(static_dir):
                        shutil.rmtree(static_dir)
                    shutil.copytree(static_backup, static_dir)
                    print(f"✅ Directorio restaurado: {static_dir}")
            
            # Limpiar directorio temporal
            shutil.rmtree(temp_dir)
            
            print(f"✅ Restauración completada desde: {backup_name}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error en restauración: {str(e)}")
            print(f"❌ Error en restauración: {str(e)}")
            return False
    
    def get_backup_status(self) -> Dict:
        """Obtener estado de los backups"""
        try:
            backups = list(self.backup_dir.glob("*.zip"))
            
            status = {
                'total_backups': len(backups),
                'total_size': sum(b.stat().st_size for b in backups),
                'latest_backup': None,
                'backup_health': 'healthy',
                'recent_backups': []
            }
            
            if backups:
                # Ordenar por fecha de modificación
                backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                latest = backups[0]
                status['latest_backup'] = {
                    'name': latest.stem,
                    'size': latest.stat().st_size,
                    'date': datetime.fromtimestamp(latest.stat().st_mtime).isoformat()
                }
                
                # Últimos 5 backups
                status['recent_backups'] = [
                    {
                        'name': b.stem,
                        'size': b.stat().st_size,
                        'date': datetime.fromtimestamp(b.stat().st_mtime).isoformat()
                    }
                    for b in backups[:5]
                ]
                
                # Verificar salud (último backup no debe ser muy antiguo)
                last_backup_age = datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)
                if last_backup_age > timedelta(days=2):
                    status['backup_health'] = 'warning'
                if last_backup_age > timedelta(days=7):
                    status['backup_health'] = 'critical'
            
            return status
            
        except Exception as e:
            return {
                'error': str(e),
                'backup_health': 'error'
            }
    
    def list_backups(self) -> List[Dict]:
        """Listar todos los backups disponibles"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*.zip"):
                backup_info = {
                    'name': backup_file.stem,
                    'file': backup_file.name,
                    'size': backup_file.stat().st_size,
                    'date': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                    'type': 'unknown'
                }
                
                # Determinar tipo de backup por el nombre
                if 'full_backup' in backup_file.stem:
                    backup_info['type'] = 'full'
                elif 'incremental_backup' in backup_file.stem:
                    backup_info['type'] = 'incremental'
                elif 'config_backup' in backup_file.stem:
                    backup_info['type'] = 'configuration'
                
                backups.append(backup_info)
            
            # Ordenar por fecha (más reciente primero)
            backups.sort(key=lambda x: x['date'], reverse=True)
            
            return backups
            
        except Exception as e:
            current_app.logger.error(f"Error listando backups: {str(e)}")
            return []

# Instancia global del servicio
backup_service = BackupService()
