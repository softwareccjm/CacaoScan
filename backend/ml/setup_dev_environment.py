"""
Script para configurar el entorno de desarrollo sin subir imágenes al repositorio.

Este script:
1. Crea los directorios necesarios
2. Verifica que las imágenes estén en .gitignore
3. Proporciona instrucciones para agregar imágenes de prueba
"""

import os
import sys
from pathlib import Path

def main():
    """Función principal para configurar el entorno."""
    
    print("🔧 CONFIGURANDO ENTORNO DE DESARROLLO CACOASCAN")
    print("=" * 60)
    
    # Directorio base del proyecto
    base_dir = Path(__file__).parent.parent
    
    # Directorios que necesitan existir
    required_dirs = [
        base_dir / 'ml' / 'media' / 'imgs',
        base_dir / 'ml' / 'media' / 'cacao_images' / 'new',
        base_dir / 'ml' / 'media' / 'dataset',
        base_dir / 'ml' / 'models',
        base_dir / 'ml' / 'runs',
        base_dir / 'ml' / 'logs',
        base_dir / 'ml' / 'outputs'
    ]
    
    print("\n📁 CREANDO DIRECTORIOS NECESARIOS")
    print("-" * 40)
    
    for dir_path in required_dirs:
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ {dir_path}")
        except Exception as e:
            print(f"❌ Error creando {dir_path}: {e}")
    
    print("\n🐍 VERIFICANDO ENTORNOS VIRTUALES")
    print("-" * 40)
    
    # Verificar que no hay entornos virtuales en el repositorio
    venv_dirs = [
        base_dir / 'venv',
        base_dir / 'env',
        base_dir / '.venv',
        base_dir / 'backend' / 'venv',
        base_dir / 'frontend' / 'node_modules'
    ]
    
    for venv_dir in venv_dirs:
        if venv_dir.exists():
            print(f"⚠️ {venv_dir} existe (correcto - no se sube al repositorio)")
        else:
            print(f"✅ {venv_dir} no existe (correcto)")
    
    print("\n📋 INSTRUCCIONES PARA ENTORNOS VIRTUALES")
    print("-" * 40)
    
    print("Para crear y usar entornos virtuales (SIN subirlos al repositorio):")
    print()
    print("1. 🐍 Crear entorno virtual de Python:")
    print(f"   python -m venv {base_dir}/venv")
    print()
    print("2. 🔌 Activar entorno virtual:")
    print("   # Windows:")
    print(f"   {base_dir}/venv/Scripts/activate")
    print("   # Linux/Mac:")
    print(f"   source {base_dir}/venv/bin/activate")
    print()
    print("3. 📦 Instalar dependencias:")
    print("   pip install -r requirements.txt")
    print()
    print("4. 🌐 Instalar dependencias de frontend:")
    print(f"   cd {base_dir}/frontend")
    print("   npm install")
    print()
    print("5. 🔍 Verificar que no se suban:")
    print("   git status")
    print("   # No deberían aparecer archivos de venv/ o node_modules/")
    
    print("\n🔍 VERIFICANDO .GITIGNORE")
    print("-" * 40)
    
    # Verificar que .gitignore existe
    gitignore_path = base_dir / '.gitignore'
    if gitignore_path.exists():
        print("✅ .gitignore encontrado")
        
        # Leer contenido
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        # Verificar que contiene las exclusiones necesarias
        required_exclusions = [
            'backend/ml/media/imgs/',
            'backend/ml/media/cacao_images/',
            'backend/ml/media/dataset/',
            'backend/ml/models/',
            '*.pt',
            '*.pth',
            'venv/',
            'env/',
            '.venv/',
            'node_modules/'
        ]
        
        missing_exclusions = []
        for exclusion in required_exclusions:
            if exclusion not in content:
                missing_exclusions.append(exclusion)
        
        if missing_exclusions:
            print("⚠️ Faltan exclusiones en .gitignore:")
            for exclusion in missing_exclusions:
                print(f"   - {exclusion}")
        else:
            print("✅ Todas las exclusiones están presentes")
    else:
        print("❌ .gitignore no encontrado")
    
    print("\n📋 INSTRUCCIONES PARA AGREGAR IMÁGENES")
    print("-" * 40)
    
    print("Para agregar imágenes de prueba (SIN subirlas al repositorio):")
    print()
    print("1. 📸 Imágenes originales del dataset:")
    print(f"   cp /ruta/a/tus/imagenes/*.bmp {base_dir}/ml/media/imgs/")
    print()
    print("2. 📊 Archivo dataset.csv:")
    print(f"   cp /ruta/a/tu/dataset.csv {base_dir}/ml/media/dataset/")
    print()
    print("3. 🔍 Verificar que no se suban:")
    print("   git status")
    print("   # No deberían aparecer archivos de imágenes")
    print()
    print("4. 🚫 Si aparecen accidentalmente:")
    print("   git rm --cached backend/ml/media/imgs/*")
    print("   git rm --cached backend/ml/media/cacao_images/*")
    print("   git rm --cached backend/ml/media/dataset/*")
    print("   git add .gitignore")
    print("   git commit -m 'Agregar imágenes al .gitignore'")
    
    print("\n🐍 INSTRUCCIONES PARA ENTORNOS VIRTUALES")
    print("-" * 40)
    
    print("Para crear y usar entornos virtuales (SIN subirlos al repositorio):")
    print()
    print("1. 🐍 Crear entorno virtual de Python:")
    print(f"   python -m venv {base_dir}/venv")
    print()
    print("2. 🔌 Activar entorno virtual:")
    print("   # Windows:")
    print(f"   {base_dir}/venv/Scripts/activate")
    print("   # Linux/Mac:")
    print(f"   source {base_dir}/venv/bin/activate")
    print()
    print("3. 📦 Instalar dependencias:")
    print("   pip install -r requirements.txt")
    print()
    print("4. 🌐 Instalar dependencias de frontend:")
    print(f"   cd {base_dir}/frontend")
    print("   npm install")
    print()
    print("5. 🔍 Verificar que no se suban:")
    print("   git status")
    print("   # No deberían aparecer archivos de venv/ o node_modules/")
    print()
    print("6. 🚫 Si aparecen accidentalmente:")
    print("   git rm --cached -r venv/")
    print("   git rm --cached -r frontend/node_modules/")
    print("   git add .gitignore")
    print("   git commit -m 'Agregar entornos virtuales al .gitignore'")
    
    print("\n🧪 CREANDO ARCHIVOS DE PRUEBA")
    print("-" * 40)
    
    # Crear archivos de ejemplo
    example_files = [
        (base_dir / 'ml' / 'media' / 'dataset' / 'dataset.csv', 
         'ID,ALTO,GROSOR,ANCHO,PESO\n1,22.5,7.2,14.8,1.95\n2,23.1,7.5,15.2,2.01\n'),
        (base_dir / 'ml' / 'media' / 'imgs' / 'README.txt',
         'Coloca aquí las imágenes originales del dataset (1.bmp, 2.bmp, etc.)\nNO hacer commit de estas imágenes al repositorio.\n'),
        (base_dir / 'ml' / 'media' / 'cacao_images' / 'new' / 'README.txt',
         'Coloca aquí las nuevas imágenes para entrenamiento incremental\nNO hacer commit de estas imágenes al repositorio.\n'),
        (base_dir / 'ml' / 'models' / 'README.txt',
         'Coloca aquí los modelos entrenados (*.pt, *.pth)\nNO hacer commit de estos archivos al repositorio.\n')
    ]
    
    for file_path, content in example_files:
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ {file_path}")
        except Exception as e:
            print(f"❌ Error creando {file_path}: {e}")
    
    print("\n🎯 VERIFICACIÓN FINAL")
    print("-" * 40)
    
    # Verificar que los directorios están vacíos de archivos de imagen
    img_dirs = [
        base_dir / 'ml' / 'media' / 'imgs',
        base_dir / 'ml' / 'media' / 'cacao_images' / 'new'
    ]
    
    for img_dir in img_dirs:
        if img_dir.exists():
            img_files = list(img_dir.glob('*.bmp')) + list(img_dir.glob('*.jpg')) + list(img_dir.glob('*.png'))
            if img_files:
                print(f"⚠️ {img_dir} contiene {len(img_files)} archivos de imagen")
                print("   Estos archivos NO se subirán al repositorio")
            else:
                print(f"✅ {img_dir} está vacío (correcto)")
    
    # Verificar entornos virtuales
    print("\n🐍 Verificando entornos virtuales:")
    venv_dirs = [
        base_dir / 'venv',
        base_dir / 'env',
        base_dir / '.venv',
        base_dir / 'frontend' / 'node_modules'
    ]
    
    for venv_dir in venv_dirs:
        if venv_dir.exists():
            print(f"⚠️ {venv_dir} existe (correcto - no se sube al repositorio)")
        else:
            print(f"✅ {venv_dir} no existe (correcto)")
    
    print("\n🚀 CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print("✅ Directorios creados")
    print("✅ .gitignore verificado")
    print("✅ Archivos de ejemplo creados")
    print("✅ Instrucciones proporcionadas")
    print()
    print("📝 PRÓXIMOS PASOS:")
    print("1. Crear entorno virtual: python -m venv venv")
    print("2. Activar entorno virtual: venv\\Scripts\\activate (Windows)")
    print("3. Instalar dependencias: pip install -r requirements.txt")
    print("4. Agregar tus imágenes de prueba a los directorios correspondientes")
    print("5. Verificar que no aparezcan en 'git status'")
    print("6. Hacer commit solo del código fuente")
    print("7. ¡Listo para desarrollar!")
    
    print("\n🔒 RECORDATORIO IMPORTANTE:")
    print("Las imágenes y entornos virtuales se mantienen SOLO en tu máquina local.")
    print("NO se suben al repositorio Git.")
    print("Solo el código fuente va al repositorio.")


if __name__ == "__main__":
    main()
