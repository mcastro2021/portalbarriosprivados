"""
Optimizador de assets (CSS, JS, imágenes)
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from flask import current_app
import cssmin
import jsmin
from PIL import Image


class AssetOptimizer:
    """Optimizador de assets estáticos"""
    
    def __init__(self, static_folder: str = 'static'):
        self.static_folder = static_folder
        self.manifest = {}
        self.manifest_file = os.path.join(static_folder, 'manifest.json')
        self._load_manifest()
    
    def _load_manifest(self):
        """Cargar manifest de assets"""
        try:
            if os.path.exists(self.manifest_file):
                with open(self.manifest_file, 'r') as f:
                    self.manifest = json.load(f)
        except Exception as e:
            current_app.logger.warning(f'Error cargando manifest: {e}')
            self.manifest = {}
    
    def _save_manifest(self):
        """Guardar manifest de assets"""
        try:
            os.makedirs(os.path.dirname(self.manifest_file), exist_ok=True)
            with open(self.manifest_file, 'w') as f:
                json.dump(self.manifest, f, indent=2)
        except Exception as e:
            current_app.logger.error(f'Error guardando manifest: {e}')
    
    def _get_file_hash(self, file_path: str) -> str:
        """Obtener hash de archivo para versionado"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()[:8]
        except Exception:
            return 'unknown'
    
    def minify_css(self, input_files: List[str], output_file: str) -> bool:
        """
        Minificar archivos CSS
        
        Args:
            input_files: Lista de archivos CSS de entrada
            output_file: Archivo CSS de salida
            
        Returns:
            bool: True si fue exitoso
        """
        try:
            combined_css = ""
            
            for input_file in input_files:
                file_path = os.path.join(self.static_folder, input_file)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        css_content = f.read()
                        
                    # Procesar URLs relativas
                    css_content = self._process_css_urls(css_content, input_file)
                    combined_css += css_content + "\n"
                else:
                    current_app.logger.warning(f'Archivo CSS no encontrado: {file_path}')
            
            # Minificar CSS
            minified_css = cssmin.cssmin(combined_css)
            
            # Añadir header con información
            header = f"/* Generated: {os.path.basename(output_file)} */\n"
            minified_css = header + minified_css
            
            # Guardar archivo minificado
            output_path = os.path.join(self.static_folder, output_file)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(minified_css)
            
            # Actualizar manifest
            file_hash = self._get_file_hash(output_path)
            versioned_name = self._add_version_to_filename(output_file, file_hash)
            versioned_path = os.path.join(self.static_folder, versioned_name)
            
            # Crear archivo versionado
            with open(versioned_path, 'w', encoding='utf-8') as f:
                f.write(minified_css)
            
            self.manifest[output_file] = {
                'versioned': versioned_name,
                'hash': file_hash,
                'size': len(minified_css),
                'sources': input_files
            }
            
            current_app.logger.info(f'CSS minificado: {output_file} -> {versioned_name}')
            return True
            
        except Exception as e:
            current_app.logger.error(f'Error minificando CSS: {e}')
            return False
    
    def minify_js(self, input_files: List[str], output_file: str) -> bool:
        """
        Minificar archivos JavaScript
        
        Args:
            input_files: Lista de archivos JS de entrada
            output_file: Archivo JS de salida
            
        Returns:
            bool: True si fue exitoso
        """
        try:
            combined_js = ""
            
            for input_file in input_files:
                file_path = os.path.join(self.static_folder, input_file)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        js_content = f.read()
                        
                    combined_js += js_content + "\n;\n"  # Añadir separador
                else:
                    current_app.logger.warning(f'Archivo JS no encontrado: {file_path}')
            
            # Minificar JavaScript
            minified_js = jsmin.jsmin(combined_js)
            
            # Añadir header con información
            header = f"/* Generated: {os.path.basename(output_file)} */\n"
            minified_js = header + minified_js
            
            # Guardar archivo minificado
            output_path = os.path.join(self.static_folder, output_file)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(minified_js)
            
            # Actualizar manifest
            file_hash = self._get_file_hash(output_path)
            versioned_name = self._add_version_to_filename(output_file, file_hash)
            versioned_path = os.path.join(self.static_folder, versioned_name)
            
            # Crear archivo versionado
            with open(versioned_path, 'w', encoding='utf-8') as f:
                f.write(minified_js)
            
            self.manifest[output_file] = {
                'versioned': versioned_name,
                'hash': file_hash,
                'size': len(minified_js),
                'sources': input_files
            }
            
            current_app.logger.info(f'JS minificado: {output_file} -> {versioned_name}')
            return True
            
        except Exception as e:
            current_app.logger.error(f'Error minificando JS: {e}')
            return False
    
    def optimize_images(self, input_dir: str = 'images', quality: int = 85) -> Dict[str, any]:
        """
        Optimizar imágenes
        
        Args:
            input_dir: Directorio de imágenes
            quality: Calidad de compresión (1-100)
            
        Returns:
            Dict con estadísticas de optimización
        """
        try:
            images_dir = os.path.join(self.static_folder, input_dir)
            if not os.path.exists(images_dir):
                return {'error': 'Directorio de imágenes no encontrado'}
            
            stats = {
                'processed': 0,
                'errors': 0,
                'original_size': 0,
                'optimized_size': 0,
                'savings': 0
            }
            
            # Formatos soportados
            supported_formats = {'.jpg', '.jpeg', '.png', '.webp'}
            
            for root, dirs, files in os.walk(images_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext in supported_formats:
                        try:
                            original_size = os.path.getsize(file_path)
                            stats['original_size'] += original_size
                            
                            # Optimizar imagen
                            with Image.open(file_path) as img:
                                # Convertir RGBA a RGB si es necesario
                                if img.mode in ('RGBA', 'LA', 'P'):
                                    background = Image.new('RGB', img.size, (255, 255, 255))
                                    if img.mode == 'P':
                                        img = img.convert('RGBA')
                                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                                    img = background
                                
                                # Crear nombre de archivo optimizado
                                name, ext = os.path.splitext(file)
                                optimized_name = f"{name}_opt{ext}"
                                optimized_path = os.path.join(root, optimized_name)
                                
                                # Guardar imagen optimizada
                                save_kwargs = {'optimize': True}
                                if file_ext in {'.jpg', '.jpeg'}:
                                    save_kwargs['quality'] = quality
                                    save_kwargs['format'] = 'JPEG'
                                elif file_ext == '.png':
                                    save_kwargs['format'] = 'PNG'
                                
                                img.save(optimized_path, **save_kwargs)
                                
                                optimized_size = os.path.getsize(optimized_path)
                                stats['optimized_size'] += optimized_size
                                
                                # Si la imagen optimizada es más pequeña, reemplazar original
                                if optimized_size < original_size:
                                    os.replace(optimized_path, file_path)
                                    savings = original_size - optimized_size
                                    stats['savings'] += savings
                                else:
                                    # Si no hay mejora, eliminar archivo optimizado
                                    os.remove(optimized_path)
                                    stats['optimized_size'] += original_size - optimized_size
                                
                                stats['processed'] += 1
                                
                        except Exception as e:
                            current_app.logger.error(f'Error optimizando imagen {file_path}: {e}')
                            stats['errors'] += 1
            
            # Calcular porcentaje de ahorro
            if stats['original_size'] > 0:
                savings_percent = (stats['savings'] / stats['original_size']) * 100
                stats['savings_percent'] = round(savings_percent, 2)
            
            current_app.logger.info(f'Optimización de imágenes completada: {stats}')
            return stats
            
        except Exception as e:
            current_app.logger.error(f'Error en optimización de imágenes: {e}')
            return {'error': str(e)}
    
    def _process_css_urls(self, css_content: str, source_file: str) -> str:
        """Procesar URLs en CSS para mantener rutas relativas correctas"""
        try:
            # Obtener directorio del archivo fuente
            source_dir = os.path.dirname(source_file)
            
            # Patrón para encontrar URLs en CSS
            url_pattern = r'url\(["\']?([^"\')\s]+)["\']?\)'
            
            def replace_url(match):
                url = match.group(1)
                
                # Si es una URL absoluta o data URI, no modificar
                if url.startswith(('http://', 'https://', 'data:', '//')):
                    return match.group(0)
                
                # Si es una ruta absoluta, no modificar
                if url.startswith('/'):
                    return match.group(0)
                
                # Construir nueva ruta relativa
                if source_dir:
                    new_url = os.path.join(source_dir, url).replace('\\', '/')
                    return f'url("{new_url}")'
                
                return match.group(0)
            
            return re.sub(url_pattern, replace_url, css_content)
            
        except Exception as e:
            current_app.logger.error(f'Error procesando URLs CSS: {e}')
            return css_content
    
    def _add_version_to_filename(self, filename: str, version: str) -> str:
        """Añadir versión al nombre de archivo"""
        name, ext = os.path.splitext(filename)
        return f"{name}.{version}{ext}"
    
    def get_asset_url(self, asset_path: str) -> str:
        """
        Obtener URL versionada de un asset
        
        Args:
            asset_path: Ruta del asset
            
        Returns:
            URL versionada del asset
        """
        if asset_path in self.manifest:
            return f"/static/{self.manifest[asset_path]['versioned']}"
        return f"/static/{asset_path}"
    
    def build_all_assets(self) -> Dict[str, any]:
        """
        Construir todos los assets del proyecto
        
        Returns:
            Dict con resultados de la construcción
        """
        try:
            results = {
                'css': [],
                'js': [],
                'images': {},
                'errors': []
            }
            
            # Configuración de assets
            asset_config = {
                'css': {
                    'app.min.css': ['css/style.css'],
                    'vendor.min.css': []  # Añadir CSS de terceros aquí
                },
                'js': {
                    'app.min.js': ['js/app.js'],
                    'vendor.min.js': []  # Añadir JS de terceros aquí
                }
            }
            
            # Minificar CSS
            for output_file, input_files in asset_config['css'].items():
                if input_files:  # Solo procesar si hay archivos
                    success = self.minify_css(input_files, f'dist/{output_file}')
                    results['css'].append({
                        'file': output_file,
                        'success': success,
                        'sources': input_files
                    })
            
            # Minificar JS
            for output_file, input_files in asset_config['js'].items():
                if input_files:  # Solo procesar si hay archivos
                    success = self.minify_js(input_files, f'dist/{output_file}')
                    results['js'].append({
                        'file': output_file,
                        'success': success,
                        'sources': input_files
                    })
            
            # Optimizar imágenes
            results['images'] = self.optimize_images()
            
            # Guardar manifest
            self._save_manifest()
            
            current_app.logger.info('Construcción de assets completada')
            return results
            
        except Exception as e:
            current_app.logger.error(f'Error construyendo assets: {e}')
            return {'error': str(e)}
    
    def clean_old_assets(self) -> int:
        """
        Limpiar assets antiguos
        
        Returns:
            Número de archivos eliminados
        """
        try:
            cleaned = 0
            dist_dir = os.path.join(self.static_folder, 'dist')
            
            if not os.path.exists(dist_dir):
                return 0
            
            # Obtener archivos actuales del manifest
            current_files = set()
            for asset_info in self.manifest.values():
                if 'versioned' in asset_info:
                    current_files.add(asset_info['versioned'])
            
            # Eliminar archivos no referenciados
            for root, dirs, files in os.walk(dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.static_folder)
                    
                    if relative_path not in current_files and file != 'manifest.json':
                        try:
                            os.remove(file_path)
                            cleaned += 1
                            current_app.logger.info(f'Asset eliminado: {relative_path}')
                        except Exception as e:
                            current_app.logger.error(f'Error eliminando {file_path}: {e}')
            
            return cleaned
            
        except Exception as e:
            current_app.logger.error(f'Error limpiando assets: {e}')
            return 0
    
    def get_stats(self) -> Dict[str, any]:
        """
        Obtener estadísticas de assets
        
        Returns:
            Dict con estadísticas
        """
        try:
            stats = {
                'total_assets': len(self.manifest),
                'assets': {},
                'total_size': 0
            }
            
            for asset_path, asset_info in self.manifest.items():
                stats['assets'][asset_path] = {
                    'versioned': asset_info.get('versioned', ''),
                    'hash': asset_info.get('hash', ''),
                    'size': asset_info.get('size', 0),
                    'sources': asset_info.get('sources', [])
                }
                stats['total_size'] += asset_info.get('size', 0)
            
            return stats
            
        except Exception as e:
            current_app.logger.error(f'Error obteniendo stats de assets: {e}')
            return {'error': str(e)}


# Función helper para usar en templates
def asset_url(asset_path: str) -> str:
    """
    Función helper para obtener URL de asset en templates
    
    Args:
        asset_path: Ruta del asset
        
    Returns:
        URL versionada del asset
    """
    try:
        optimizer = AssetOptimizer()
        return optimizer.get_asset_url(asset_path)
    except Exception:
        return f"/static/{asset_path}"
