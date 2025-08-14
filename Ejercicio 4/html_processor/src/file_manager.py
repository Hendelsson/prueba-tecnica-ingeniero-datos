import os
from pathlib import Path
from typing import List, Union


class FileManager:
    """Maneja la búsqueda y gestión de archivos HTML."""
    
    @staticmethod
    def get_html_files(paths: List[Union[str, Path]]) -> List[Path]:
        """
        Obtiene una lista de archivos HTML desde archivos individuales o directorios.
        
        Args:
            paths: Lista de rutas que pueden ser archivos o directorios
            
        Returns:
            Lista de objetos Path que apuntan a archivos HTML
        """
        html_files = []
        
        for path_str in paths:
            path = Path(path_str)
            
            if not path.exists():
                print(f"Advertencia: La ruta {path} no existe")
                continue
                
            if path.is_file() and path.suffix.lower() == '.html':
                html_files.append(path)
            elif path.is_dir():
                # Buscar recursivamente archivos HTML en el directorio
                html_files.extend(path.rglob('*.html'))
                
        return list(set(html_files))  # Eliminar duplicados
    
    @staticmethod
    def create_output_filename(original_path: Path, output_dir: Path) -> Path:
        """
        Crea el nombre del archivo de salida basado en el archivo original.
        
        Args:
            original_path: Ruta del archivo original
            output_dir: Directorio de salida
            
        Returns:
            Ruta completa del archivo de salida
        """
        stem = original_path.stem
        suffix = original_path.suffix
        return output_dir / f"{stem}_processed{suffix}"