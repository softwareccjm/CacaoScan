# 📁 Gestión de Archivos - CacaoScan

## 🚫 Archivos que NO se suben al repositorio

### Imágenes de Entrenamiento
- `backend/ml/media/imgs/` - Imágenes originales del dataset
- `backend/ml/media/cacao_images/` - Imágenes de nuevas muestras
- `backend/media/cacao_images/` - Imágenes subidas por usuarios
- `backend/media/imgs/` - Imágenes procesadas

### Modelos Entrenados
- `backend/ml/models/` - Modelos YOLOv8 entrenados
- `*.pt`, `*.pth`, `*.pkl`, `*.h5`, `*.onnx` - Archivos de modelos

### Datos de Entrenamiento
- `backend/ml/media/dataset/` - Archivos CSV del dataset
- `backend/ml/runs/` - Logs de entrenamiento
- `backend/ml/logs/` - Archivos de log
- `backend/ml/outputs/` - Resultados de entrenamiento

### Entornos Virtuales
- `venv/` - Entorno virtual de Python
- `env/` - Entorno virtual alternativo
- `.venv/` - Entorno virtual oculto
- `pyvenv.cfg` - Configuración del entorno virtual
- `frontend/node_modules/` - Dependencias de Node.js

### Archivos de Configuración Local

### Código Fuente
- `backend/ml/*.py` - Scripts de Python
- `frontend/src/` - Código Vue.js
- `backend/apps/` - Código Django
- `backend/config/` - Configuración Django

### Documentación
- `*.md` - Archivos README y documentación
- `*.txt` - Archivos de texto
- `*.json` - Archivos de configuración

### Configuración
- `requirements.txt` - Dependencias Python
- `package.json` - Dependencias Node.js
- `settings.py` - Configuración Django

## 🐍 Cómo trabajar con entornos virtuales

### 1. Crear entorno virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Activar entorno virtual (Linux/Mac)
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Instalar dependencias Node.js
cd frontend
npm install
```

### 3. Verificar que no se suban
```bash
# Verificar que el entorno virtual está en .gitignore
git status
# No deberían aparecer archivos de venv/
```

### 4. Si aparecen accidentalmente
```bash
# Remover del índice de Git (pero mantener en disco)
git rm --cached -r venv/
git rm --cached -r frontend/node_modules/

# Hacer commit de la remoción
git add .gitignore
git commit -m "Agregar entornos virtuales al .gitignore"
```

## 🔧 Cómo trabajar con imágenes

### 1. Preparar el entorno local
```bash
# Crear directorios necesarios
mkdir -p backend/ml/media/imgs
mkdir -p backend/ml/media/cacao_images/new
mkdir -p backend/ml/media/dataset
mkdir -p backend/ml/models
```

### 2. Agregar imágenes de prueba
```bash
# Copiar imágenes de prueba (NO hacer commit)
cp /ruta/a/tus/imagenes/*.bmp backend/ml/media/imgs/
cp /ruta/a/tu/dataset.csv backend/ml/media/dataset/
```

### 3. Verificar que no se suban
```bash
# Verificar que las imágenes están en .gitignore
git status
# No deberían aparecer archivos de imágenes
```

### 4. Si accidentalmente se agregaron
```bash
# Remover del índice de Git (pero mantener en disco)
git rm --cached backend/ml/media/imgs/*
git rm --cached backend/ml/media/cacao_images/*
git rm --cached backend/ml/media/dataset/*

# Hacer commit de la remoción
git add .gitignore
git commit -m "Agregar imágenes al .gitignore"
```

## 📋 Estructura de Directorios

```
backend/ml/
├── media/                    # 🚫 NO subir
│   ├── imgs/                # Imágenes originales
│   ├── cacao_images/        # Imágenes de nuevas muestras
│   └── dataset/             # Archivos CSV
├── models/                  # 🚫 NO subir
│   ├── weight_yolo.pt       # Modelo entrenado
│   └── *.pth                # Otros modelos
├── runs/                    # 🚫 NO subir
│   └── train/               # Logs de entrenamiento
├── logs/                    # 🚫 NO subir
│   └── *.log                # Archivos de log
├── *.py                     # ✅ SÍ subir
├── *.md                     # ✅ SÍ subir
└── .gitignore               # ✅ SÍ subir
```

## 🚨 Importante

### ❌ NO hacer:
- `git add backend/ml/media/imgs/*`
- `git add backend/ml/models/*.pt`
- `git add backend/ml/media/dataset/*.csv`
- Subir archivos de imágenes al repositorio

### ✅ SÍ hacer:
- `git add backend/ml/*.py`
- `git add backend/ml/*.md`
- `git add .gitignore`
- Mantener las imágenes solo localmente

## 🔄 Flujo de trabajo recomendado

1. **Desarrollo local**: Trabajar con imágenes locales
2. **Testing**: Usar imágenes de prueba pequeñas
3. **Commit**: Solo código fuente y documentación
4. **Deploy**: Configurar imágenes en servidor de producción
5. **Backup**: Hacer backup separado de imágenes importantes

## 📞 Soporte

Si tienes problemas con archivos que se suben accidentalmente:

1. Revisar `.gitignore`
2. Remover archivos del índice: `git rm --cached <archivo>`
3. Hacer commit de la corrección
4. Verificar con `git status`

---

**¡Recuerda: Las imágenes se mantienen locales, solo el código va al repositorio!** 📸🚫📁✅
