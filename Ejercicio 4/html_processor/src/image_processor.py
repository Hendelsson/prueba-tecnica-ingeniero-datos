import base64
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Tuple, Optional


class ImageProcessor:
    """Procesa imágenes convirtiéndolas a base64."""
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
    
    @staticmethod
    def get_mime_type(file_path: Path) -> str:
        """
        Determina el tipo MIME basado en la extensión del archivo.
        
        Args:
            file_path: Ruta del archivo de imagen
            
        Returns:
            String con el tipo MIME
        """
        extension = file_path.suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml'
        }
        return mime_types.get(extension, 'image/jpeg')
    
    @staticmethod
    def is_supported_image(src: str) -> bool:
        """
        Verifica si la imagen tiene una extensión soportada.
        
        Args:
            src: URL o ruta de la imagen
            
        Returns:
            True si la extensión está soportada
        """
        try:
            parsed = urllib.parse.urlparse(src)
            path = Path(parsed.path)
            return path.suffix.lower() in ImageProcessor.SUPPORTED_EXTENSIONS
        except:
            return False
    
    @staticmethod
    def convert_to_base64(image_path: Path, html_dir: Path) -> Tuple[Optional[str], Optional[str]]:
        """
        Convierte una imagen a base64.
        
        Args:
            image_path: Ruta de la imagen (puede ser relativa)
            html_dir: Directorio del archivo HTML (para resolver rutas relativas)
            
        Returns:
            Tupla (base64_string, error_message)
        """
        try:
            # Resolver ruta relativa
            if not image_path.is_absolute():
                absolute_path = html_dir / image_path
            else:
                absolute_path = image_path
            
            if not absolute_path.exists():
                return None, f"Archivo no encontrado: {absolute_path}"
            
            # Leer archivo y convertir a base64
            with open(absolute_path, 'rb') as image_file:
                image_data = image_file.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                
            mime_type = ImageProcessor.get_mime_type(absolute_path)
            return f"data:{mime_type};base64,{base64_data}", None
            
        except Exception as e:
            return None, f"Error al procesar {image_path}: {str(e)}"