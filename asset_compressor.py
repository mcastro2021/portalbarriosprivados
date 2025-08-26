"""
Compresor de Assets
Optimización de CSS, JS e imágenes para mejor performance
"""

import os
import re
import gzip
import hashlib
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AssetCompressor:
    """Compresor de assets para optimización de performance"""
    
    def __init__(self, static_folder='static', output_folder='static/compressed'):
        self.static_folder = Path(static_folder)
        self.output_folder = Path(output_folder)
        self.manifest_file = self.output_folder / 'manifest.json'
        self.manifest = self.load_manifest()
        
        # Crear directorio de salida si no existe
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def load_manifest(self) -> Dict:
        """Cargar manifest de assets comprimidos"""
        if self.manifest_file.exists():
            try:
                import json
                with open(self.manifest_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_manifest(self):
        """Guardar manifest de assets"""
        import json
        with open(self.manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def compress_all_assets(self):
        """Comprimir todos los assets"""
        logger.info("🚀 Iniciando compresión de assets...")
        
        # Comprimir CSS
        css_files = self.find_files('*.css')
        for css_file in css_files:
            self.compress_css(css_file)
        
        # Comprimir JS
        js_files = self.find_files('*.js')
        for js_file in js_files:
            self.compress_js(js_file)
        
        # Optimizar imágenes
        image_files = self.find_files('*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp')
        for image_file in image_files:
            self.optimize_image(image_file)
        
        # Generar manifest
        self.save_manifest()
        
        logger.info("✅ Compresión de assets completada")
    
    def find_files(self, *patterns) -> List[Path]:
        """Encontrar archivos que coincidan con patrones"""
        files = []
        for pattern in patterns:
            files.extend(self.static_folder.rglob(pattern))
        return files
    
    def compress_css(self, css_file: Path):
        """Comprimir archivo CSS"""
        try:
            # Leer archivo CSS
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Comprimir CSS
            compressed_content = self.minify_css(content)
            
            # Generar nombre de archivo comprimido
            relative_path = css_file.relative_to(self.static_folder)
            compressed_file = self.output_folder / relative_path
            
            # Crear directorio si no existe
            compressed_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar archivo comprimido
            with open(compressed_file, 'w', encoding='utf-8') as f:
                f.write(compressed_content)
            
            # Crear versión gzipped
            gzip_file = compressed_file.with_suffix(compressed_file.suffix + '.gz')
            with gzip.open(gzip_file, 'wt', encoding='utf-8') as f:
                f.write(compressed_content)
            
            # Actualizar manifest
            self.manifest[str(relative_path)] = {
                'original_size': len(content),
                'compressed_size': len(compressed_content),
                'gzipped_size': os.path.getsize(gzip_file),
                'compressed_at': datetime.now().isoformat(),
                'hash': self.calculate_hash(compressed_content)
            }
            
            logger.info(f"✅ CSS comprimido: {relative_path}")
            
        except Exception as e:
            logger.error(f"❌ Error comprimiendo CSS {css_file}: {e}")
    
    def minify_css(self, content: str) -> str:
        """Minificar contenido CSS"""
        # Remover comentarios
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remover espacios en blanco innecesarios
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r';\s*}', '}', content)
        content = re.sub(r'{\s*', '{', content)
        content = re.sub(r'}\s*', '}', content)
        content = re.sub(r':\s*', ':', content)
        content = re.sub(r';\s*', ';', content)
        content = re.sub(r',\s*', ',', content)
        
        # Remover espacios al inicio y final
        content = content.strip()
        
        return content
    
    def compress_js(self, js_file: Path):
        """Comprimir archivo JavaScript"""
        try:
            # Leer archivo JS
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Comprimir JS
            compressed_content = self.minify_js(content)
            
            # Generar nombre de archivo comprimido
            relative_path = js_file.relative_to(self.static_folder)
            compressed_file = self.output_folder / relative_path
            
            # Crear directorio si no existe
            compressed_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar archivo comprimido
            with open(compressed_file, 'w', encoding='utf-8') as f:
                f.write(compressed_content)
            
            # Crear versión gzipped
            gzip_file = compressed_file.with_suffix(compressed_file.suffix + '.gz')
            with gzip.open(gzip_file, 'wt', encoding='utf-8') as f:
                f.write(compressed_content)
            
            # Actualizar manifest
            self.manifest[str(relative_path)] = {
                'original_size': len(content),
                'compressed_size': len(compressed_content),
                'gzipped_size': os.path.getsize(gzip_file),
                'compressed_at': datetime.now().isoformat(),
                'hash': self.calculate_hash(compressed_content)
            }
            
            logger.info(f"✅ JS comprimido: {relative_path}")
            
        except Exception as e:
            logger.error(f"❌ Error comprimiendo JS {js_file}: {e}")
    
    def minify_js(self, content: str) -> str:
        """Minificar contenido JavaScript"""
        # Remover comentarios de una línea
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # Remover comentarios multilínea
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remover espacios en blanco innecesarios
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r';\s*}', '}', content)
        content = re.sub(r'{\s*', '{', content)
        content = re.sub(r'}\s*', '}', content)
        content = re.sub(r'\(\s*', '(', content)
        content = re.sub(r'\s*\)', ')', content)
        content = re.sub(r'\[\s*', '[', content)
        content = re.sub(r'\s*\]', ']', content)
        
        # Remover espacios al inicio y final
        content = content.strip()
        
        return content
    
    def optimize_image(self, image_file: Path):
        """Optimizar imagen"""
        try:
            from PIL import Image, ImageOps
            
            # Abrir imagen
            with Image.open(image_file) as img:
                # Convertir a RGB si es necesario
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Optimizar calidad
                optimized_file = self.output_folder / image_file.relative_to(self.static_folder)
                optimized_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Guardar imagen optimizada
                img.save(optimized_file, optimize=True, quality=85)
                
                # Crear versión WebP si es posible
                webp_file = optimized_file.with_suffix('.webp')
                img.save(webp_file, 'WEBP', quality=85)
                
                # Actualizar manifest
                relative_path = image_file.relative_to(self.static_folder)
                self.manifest[str(relative_path)] = {
                    'original_size': image_file.stat().st_size,
                    'optimized_size': optimized_file.stat().st_size,
                    'webp_size': webp_file.stat().st_size,
                    'optimized_at': datetime.now().isoformat(),
                    'dimensions': f"{img.width}x{img.height}"
                }
                
                logger.info(f"✅ Imagen optimizada: {relative_path}")
                
        except ImportError:
            logger.warning("⚠️ PIL no disponible, saltando optimización de imágenes")
        except Exception as e:
            logger.error(f"❌ Error optimizando imagen {image_file}: {e}")
    
    def calculate_hash(self, content: str) -> str:
        """Calcular hash del contenido"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_asset_url(self, asset_path: str, use_compressed: bool = True) -> str:
        """Obtener URL del asset (comprimido o original)"""
        if use_compressed and asset_path in self.manifest:
            return f"/static/compressed/{asset_path}"
        return f"/static/{asset_path}"
    
    def get_asset_hash(self, asset_path: str) -> Optional[str]:
        """Obtener hash del asset para cache busting"""
        if asset_path in self.manifest:
            return self.manifest[asset_path].get('hash', '')
        return None
    
    def generate_asset_tags(self, assets: List[str], use_compressed: bool = True) -> str:
        """Generar tags HTML para assets"""
        tags = []
        
        for asset in assets:
            if asset.endswith('.css'):
                url = self.get_asset_url(asset, use_compressed)
                hash_value = self.get_asset_hash(asset)
                hash_param = f"?v={hash_value}" if hash_value else ""
                tags.append(f'<link rel="stylesheet" href="{url}{hash_param}">')
            
            elif asset.endswith('.js'):
                url = self.get_asset_url(asset, use_compressed)
                hash_value = self.get_asset_hash(asset)
                hash_param = f"?v={hash_value}" if hash_value else ""
                tags.append(f'<script src="{url}{hash_param}"></script>')
        
        return '\n'.join(tags)
    
    def get_compression_stats(self) -> Dict:
        """Obtener estadísticas de compresión"""
        total_original = 0
        total_compressed = 0
        total_gzipped = 0
        
        for asset_info in self.manifest.values():
            total_original += asset_info.get('original_size', 0)
            total_compressed += asset_info.get('compressed_size', 0)
            total_gzipped += asset_info.get('gzipped_size', 0)
        
        return {
            'total_assets': len(self.manifest),
            'total_original_size': total_original,
            'total_compressed_size': total_compressed,
            'total_gzipped_size': total_gzipped,
            'compression_ratio': (1 - total_compressed / total_original) * 100 if total_original > 0 else 0,
            'gzip_ratio': (1 - total_gzipped / total_original) * 100 if total_original > 0 else 0
        }

class AssetBundler:
    """Bundler de assets para combinar múltiples archivos"""
    
    def __init__(self, static_folder='static', output_folder='static/bundled'):
        self.static_folder = Path(static_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def create_css_bundle(self, bundle_name: str, css_files: List[str]):
        """Crear bundle de CSS"""
        bundle_content = []
        
        for css_file in css_files:
            file_path = self.static_folder / css_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Agregar comentario con nombre del archivo
                    bundle_content.append(f"/* {css_file} */")
                    bundle_content.append(content)
        
        # Guardar bundle
        bundle_file = self.output_folder / f"{bundle_name}.css"
        with open(bundle_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(bundle_content))
        
        logger.info(f"✅ Bundle CSS creado: {bundle_name}.css")
        return bundle_file
    
    def create_js_bundle(self, bundle_name: str, js_files: List[str]):
        """Crear bundle de JavaScript"""
        bundle_content = []
        
        for js_file in js_files:
            file_path = self.static_folder / js_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Agregar comentario con nombre del archivo
                    bundle_content.append(f"// {js_file}")
                    bundle_content.append(content)
        
        # Guardar bundle
        bundle_file = self.output_folder / f"{bundle_name}.js"
        with open(bundle_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(bundle_content))
        
        logger.info(f"✅ Bundle JS creado: {bundle_name}.js")
        return bundle_file

# Instancia global del compresor
asset_compressor = AssetCompressor()
asset_bundler = AssetBundler()

def compress_assets():
    """Función de conveniencia para comprimir assets"""
    asset_compressor.compress_all_assets()

def create_bundles():
    """Crear bundles de assets"""
    # Bundle CSS principal
    css_bundle_files = [
        'css/bootstrap.min.css',
        'css/app.css',
        'css/components.css'
    ]
    asset_bundler.create_css_bundle('main', css_bundle_files)
    
    # Bundle JS principal
    js_bundle_files = [
        'js/app.js',
        'js/components.js',
        'js/performance-optimizer.js'
    ]
    asset_bundler.create_js_bundle('main', js_bundle_files)

if __name__ == '__main__':
    # Comprimir assets
    compress_assets()
    
    # Crear bundles
    create_bundles()
    
    # Mostrar estadísticas
    stats = asset_compressor.get_compression_stats()
    print(f"📊 Estadísticas de compresión:")
    print(f"   Total de assets: {stats['total_assets']}")
    print(f"   Tamaño original: {stats['total_original_size'] / 1024:.1f} KB")
    print(f"   Tamaño comprimido: {stats['total_compressed_size'] / 1024:.1f} KB")
    print(f"   Tamaño gzipped: {stats['total_gzipped_size'] / 1024:.1f} KB")
    print(f"   Ratio de compresión: {stats['compression_ratio']:.1f}%")
    print(f"   Ratio gzip: {stats['gzip_ratio']:.1f}%")
