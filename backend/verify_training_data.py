"""
Script para verificar que el código de entrenamiento lee correctamente
las imágenes desde raw y los datos del CSV.
"""
import os
import sys
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
import django
django.setup()

from ml.data.dataset_loader import CacaoDatasetLoader
from ml.utils.paths import get_raw_images_dir, get_datasets_dir

def main():
    print("=" * 60)
    print("VERIFICACIÓN DE DATOS PARA ENTRENAMIENTO")
    print("=" * 60)
    
    # 1. Verificar directorio de imágenes raw
    print("\n1. Verificando directorio de imágenes raw...")
    raw_dir = get_raw_images_dir()
    print(f"   Directorio raw: {raw_dir}")
    print(f"   Existe: {raw_dir.exists()}")
    
    if raw_dir.exists():
        bmp_files = list(raw_dir.glob("*.bmp"))
        print(f"   Archivos .bmp encontrados: {len(bmp_files)}")
        if bmp_files:
            print(f"   Ejemplos: {[f.name for f in bmp_files[:5]]}")
    
    # 2. Verificar CSV
    print("\n2. Verificando archivo CSV...")
    datasets_dir = get_datasets_dir()
    csv_files = list(datasets_dir.glob("*.csv"))
    print(f"   Directorio datasets: {datasets_dir}")
    print(f"   Archivos CSV encontrados: {len(csv_files)}")
    for csv_file in csv_files:
        print(f"   - {csv_file.name}")
    
    # 3. Cargar dataset
    print("\n3. Cargando dataset...")
    try:
        loader = CacaoDatasetLoader()
        print(f"   CSV usado: {loader.csv_path}")
        
        df = loader.load_dataset()
        print(f"   Total registros en CSV: {len(df)}")
        print(f"   Columnas: {list(df.columns)}")
        print(f"\n   Primeros 5 registros:")
        print(df.head()[['id', 'alto', 'ancho', 'grosor', 'peso']].to_string())
        
        # 4. Validar imágenes
        print("\n4. Validando existencia de imágenes...")
        valid_df, missing_ids = loader.validate_images_exist(df)
        print(f"   Imágenes válidas: {len(valid_df)}")
        print(f"   Imágenes faltantes: {len(missing_ids)}")
        
        if missing_ids:
            print(f"   IDs faltantes (primeros 10): {missing_ids[:10]}")
        
        if len(valid_df) > 0:
            print(f"\n   Primeras 5 imágenes válidas:")
            print(valid_df.head()[['id', 'alto', 'ancho', 'grosor', 'peso', 'image_path']].to_string())
            
            # Verificar que las rutas apuntan a raw
            print("\n5. Verificando rutas de imágenes...")
            sample_paths = valid_df.head()['image_path'].tolist()
            for path_str in sample_paths:
                path = Path(path_str)
                exists = path.exists()
                is_raw = 'raw' in str(path)
                print(f"   {path.name}: existe={exists}, es_raw={is_raw}")
        
        # 6. Obtener registros válidos
        print("\n6. Obteniendo registros válidos completos...")
        valid_records = loader.get_valid_records()
        print(f"   Total registros válidos: {len(valid_records)}")
        
        if valid_records:
            print(f"\n   Ejemplo de registro válido:")
            sample = valid_records[0]
            print(f"   ID: {sample['id']}")
            print(f"   Alto: {sample['alto']}, Ancho: {sample['ancho']}, Grosor: {sample['grosor']}, Peso: {sample['peso']}")
            print(f"   Ruta imagen raw: {sample['raw_image_path']}")
            print(f"   Existe imagen raw: {Path(sample['raw_image_path']).exists()}")
            print(f"   Ruta crop: {sample['crop_image_path']}")
            print(f"   Existe crop: {Path(sample['crop_image_path']).exists()}")
        
        print("\n" + "=" * 60)
        print("VERIFICACIÓN COMPLETADA")
        print("=" * 60)
        print(f"\nResumen:")
        print(f"  - Imágenes raw disponibles: {len(bmp_files) if raw_dir.exists() else 0}")
        print(f"  - Registros en CSV: {len(df)}")
        print(f"  - Registros válidos (con imagen): {len(valid_df)}")
        print(f"  - Registros con crops: {sum(1 for r in valid_records if Path(r['crop_image_path']).exists())}")
        print(f"  - Registros sin crops: {sum(1 for r in valid_records if not Path(r['crop_image_path']).exists())}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

