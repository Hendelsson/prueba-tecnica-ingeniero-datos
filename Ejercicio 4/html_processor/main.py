from pathlib import Path
from src.html_processor import HTMLProcessor


def main():
    """Función principal del programa."""
    print("=== Procesador de Imágenes HTML ===")
    print()
    
    # Configurar rutas a procesar
    paths_to_process = [
        "tests/sample_files",  # Directorio con archivos HTML
        # "ruta/a/archivo.html",  # Archivo individual
        # "otro/directorio",      # Otro directorio
    ]
    
    # Crear procesador
    processor = HTMLProcessor(output_dir="output")
    
    # Procesar archivos
    results = processor.process_paths(paths_to_process)
    
    # Mostrar resumen
    print("\n=== RESUMEN DE PROCESAMIENTO ===")
    print(f"Archivos procesados exitosamente: {len(results['success'])}")
    print(f"Archivos con errores: {len(results['fail'])}")
    
    if results["success"]:
        print("\n--- Archivos exitosos ---")
        for file_path, info in results["success"].items():
            print(f"  📄 {file_path}")
            print(f"     → Salida: {info['output_file']}")
            print(f"     → Imágenes procesadas: {len(info['images_processed'])}")
            if info['images_failed']:
                print(f"     → Imágenes fallidas: {len(info['images_failed'])}")
    
    if results["fail"]:
        print("\n--- Archivos con errores ---")
        for file_path, error in results["fail"].items():
            print(f"  ❌ {file_path}: {error}")
    
    print(f"\nLos archivos procesados se encuentran en: {processor.output_dir}")


if __name__ == "__main__":
    main()