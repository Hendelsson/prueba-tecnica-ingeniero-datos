import re
from pathlib import Path
from typing import Dict, List, Any
from .file_manager import FileManager
from .image_processor import ImageProcessor


class HTMLProcessor:
    """Procesador principal de archivos HTML."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Inicializa el procesador HTML.
        
        Args:
            output_dir: Directorio donde se guardarán los archivos procesados
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {"success": {}, "fail": {}}
    
    def process_paths(self, paths: List[str]) -> Dict[str, Any]:
        """
        Procesa una lista de rutas (archivos o directorios).
        
        Args:
            paths: Lista de rutas a procesar
            
        Returns:
            Diccionario con resultados del procesamiento
        """
        html_files = FileManager.get_html_files(paths)
        
        if not html_files:
            print("No se encontraron archivos HTML para procesar.")
            return self.results
        
        print(f"Procesando {len(html_files)} archivos HTML...")
        
        for html_file in html_files:
            self._process_single_file(html_file)
        
        return self.results
    
    def _process_single_file(self, html_file: Path) -> None:
        """
        Procesa un archivo HTML individual.
        
        Args:
            html_file: Ruta del archivo HTML a procesar
        """
        try:
            print(f"Procesando: {html_file}")
            
            # Leer contenido del archivo HTML
            with open(html_file, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            # Procesar imágenes
            processed_content, file_results = self._process_images_in_html(
                html_content, html_file.parent
            )
            
            # Crear archivo de salida
            output_file = FileManager.create_output_filename(html_file, self.output_dir)
            
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(processed_content)
            
            # Registrar resultados
            file_key = str(html_file)
            self.results["success"][file_key] = {
                "output_file": str(output_file),
                "images_processed": file_results["success"],
                "images_failed": file_results["fail"]
            }
            
            print(f"  ✓ Procesado exitosamente. Salida: {output_file}")
            print(f"  ✓ Imágenes procesadas: {len(file_results['success'])}")
            if file_results["fail"]:
                print(f"  ⚠ Imágenes fallidas: {len(file_results['fail'])}")
                
        except Exception as e:
            file_key = str(html_file)
            self.results["fail"][file_key] = str(e)
            print(f"  ✗ Error procesando {html_file}: {e}")
    
    def _process_images_in_html(self, html_content: str, html_dir: Path) -> tuple:
        """
        Procesa todas las imágenes en el contenido HTML.
        
        Args:
            html_content: Contenido del archivo HTML
            html_dir: Directorio del archivo HTML
            
        Returns:
            Tupla (html_procesado, resultados)
        """
        # Patrón regex para encontrar tags <img>
        img_pattern = re.compile(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE)
        
        results = {"success": [], "fail": []}
        processed_content = html_content
        
        # Encontrar todas las imágenes
        for match in img_pattern.finditer(html_content):
            full_tag = match.group(0)
            src = match.group(1)
            
            # Saltar si ya es base64 o es una URL remota
            if src.startswith('data:') or src.startswith('http'):
                continue
            
            # Verificar si es una imagen soportada
            if not ImageProcessor.is_supported_image(src):
                results["fail"].append({
                    "src": src,
                    "error": "Formato de imagen no soportado"
                })
                continue
            
            # Convertir a base64
            image_path = Path(src)
            base64_data, error = ImageProcessor.convert_to_base64(image_path, html_dir)
            
            if base64_data:
                # Reemplazar en el HTML
                new_tag = full_tag.replace(f'src="{src}"', f'src="{base64_data}"')
                new_tag = new_tag.replace(f"src='{src}'", f"src='{base64_data}'")
                processed_content = processed_content.replace(full_tag, new_tag)
                
                results["success"].append({
                    "original_src": src,
                    "converted": True
                })
            else:
                results["fail"].append({
                    "src": src,
                    "error": error
                })
        
        return processed_content, results