# 🌱 CacaoScan — Plataforma de Análisis Digital de Granos de Cacao

**CacaoScan** es un sistema web desarrollado por aprendices del **SENA (Tecnólogo ADSO)** que permite registrar, analizar y gestionar información de productores de cacao mediante **visión por computadora, aprendizaje automático (PyTorch, YOLOv8)** y un panel administrativo interactivo.

---

## 🚀 Tecnologías Principales

| Componente | Tecnología | Descripción |
|-------------|-------------|-------------|
| **Backend** | Django 4.2 + Django REST Framework | API REST principal y gestión de modelos ML |
| **Base de Datos** | PostgreSQL 15 | Base de datos relacional |
| **Frontend** | Vue.js 3 + Vite + Pinia + TailwindCSS + Flowbite | Interfaz web moderna y responsive |
| **ML/IA** | PyTorch, scikit-learn, YOLOv8, OpenCV | Procesamiento de imágenes y predicción de peso y dimensiones |
| **Autenticación** | JWT (JSON Web Tokens) | Inicio de sesión seguro con roles y permisos |
| **Despliegue** | Render / Railway / Docker (opcional) | Listo para producción |

---

## 🧠 Funcionalidades Clave

- 🔐 Registro, autenticación y roles de usuario (admin, agricultor, técnico)
- 🌾 Gestión de fincas y lotes agrícolas
- 📷 Escaneo y análisis de granos de cacao con IA
- 📊 Reportes descargables en Excel (agricultores, usuarios, métricas)
- 🧾 Sistema de auditoría y notificaciones
- ⚙️ Configuración y calibración de modelos ML desde panel administrativo

---

## 🖥️ Requisitos Previos

Asegúrate de tener instalados:

| Requisito | Versión recomendada |
|------------|--------------------|
| Python | 3.12 o superior |
| Node.js | 18 o superior |
| PostgreSQL | 15 o superior |
| Git | Última versión estable |
| PowerShell o Bash | (para comandos de terminal) |

---

## ⚙️ Instalación del Proyecto

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/tu_usuario/cacaoscan.git
cd cacaoscan
```

### 2️⃣ Configurar el Backend (Django)

⚠️ **Asegúrate de tener instalado Python 3.12** (no versiones anteriores ni posteriores, para evitar incompatibilidades con dependencias del proyecto).

Si tienes varias versiones instaladas, usa siempre el comando `python3.12`.  
Puedes verificar tu versión con:

```bash
python3.12 --version
```

Si necesitas instalar Python 3.12, revisa la documentación oficial según tu sistema operativo: https://www.python.org/downloads/release/python-3120/


```bash
cd backend
python -3.12 -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
# source venv/bin/activate

pip install -r requirements.txt
```

Crea el archivo `.env` en la carpeta `backend/` con el siguiente contenido:

```env
DEBUG=True
SECRET_KEY=tu_clave_segura
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=cacaoscan_db
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

Aplica las migraciones:

```bash
python manage.py makemigrations
python manage.py migrate
```

Aplica los seeders

```bash
python manage.py init_catalogos
python manage.py seed_colombia
```

Crea el superusuario:

```bash
python manage.py createsuperuser
```

Inicia el servidor:

```bash
python manage.py runserver
```

✅ El backend estará disponible en: **http://127.0.0.1:8000**

### 3️⃣ Configurar el Frontend (Vue)

```bash
cd ../frontend
pnpm install
pnpm dev
```

✅ El frontend estará disponible en: **http://127.0.0.1:5173**

---

## 🐳 Instalación con Docker (Recomendado)

La forma más fácil de ejecutar CacaoScan es usando Docker Compose.

### Requisitos
- Docker Desktop instalado ([descargar aquí](https://www.docker.com/products/docker-desktop))
- Docker Compose v3.8 o superior

### Pasos de instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/tu_usuario/cacaoscan.git
cd cacaoscan
```

2. **Configurar variables de entorno**:
```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita el archivo .env con tus configuraciones (opcional)
```

3. **Construir y ejecutar los contenedores**:
```bash
docker-compose up -d --build
```

4. **Verificar que todo esté funcionando**:
```bash
docker-compose ps
docker-compose logs -f
```

5. **Acceder a la aplicación**:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1/
- **Admin Django**: http://localhost:8000/admin/

### Comandos útiles de Docker

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ borra datos)
docker-compose down -v

# Reiniciar un servicio específico
docker-compose restart backend

# Ejecutar comandos Django en el contenedor
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Reconstruir las imágenes
docker-compose build --no-cache


---

#### Pasos adicionales recomendados **antes de ejecutar pipelines de ML/IA**:

### 📸 Preparación previa antes de ejecutar pipelines de ML/IA

1. **Coloca las imágenes en la carpeta `raw`:**  
   Asegúrate de que todas las imágenes sean archivos `.bmp` y estén ubicadas dentro de la carpeta correspondiente (`cacao_images/raw/`).

2. **Agrega el dataset CSV:**  
   Copia el archivo CSV del dataset en la carpeta `datasets/`. Debe tener la siguiente estructura de columnas (la cabecera y un ejemplo):

   ```
   ID,ALTO,ANCHO,GROSOR,PESO,filename,image_path
   510,22.8,16.3,10.2,1.72,510.bmp,cacao_images\raw\510.bmp
   ```

3. **Procesa las imágenes para eliminar el fondo:**  
   Ejecuta el siguiente comando para segmentar las imágenes desde el contenedor `backend`:

   ```bash
   docker compose exec backend python manage.py calibrate_dataset_pixels --segmentation-backend auto
   ```
4. **Entrena los modelos de ML/IA:**  
   Ejecuta el siguiente comando para iniciar el entrenamiento de los modelos (puedes personalizar los argumentos según tus necesidades):

   ```bash
   docker compose exec backend python manage.py train_cacao_models --hybrid --use-pixel-features --epochs 50 --batch-size 32 --segmentation-backend opencv
   ```

   Si deseas ver todas las opciones disponibles, ejecuta:

   ```bash
   docker compose exec backend python manage.py train_cacao_models --help
   ```


```

## 📂 Estructura del Proyecto

```
cacaoscan/
├── backend/
│   ├── api/
│   ├── personas/
│   ├── fincas_app/
│   ├── reports/
│   ├── legal/               # Términos y política de privacidad
│   ├── cacaoscan/settings.py
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   ├── router/
│   │   └── services/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## 📦 Scripts Útiles

### Backend

| Comando | Descripción |
|---------|-------------|
| `python manage.py runserver` | Ejecuta el servidor de desarrollo |
| `python manage.py shell` | Abre la consola interactiva Django |
| `python manage.py showmigrations` | Lista migraciones aplicadas |
| `python manage.py createsuperuser` | Crea un administrador |

### Frontend

| Comando | Descripción |
|---------|-------------|
| `pnpm dev` | Inicia el servidor de desarrollo |
| `pnpm build` | Genera la versión de producción |
| `pnpm preview` | Previsualiza el build localmente |

---

## 🧩 Endpoints Principales

| Endpoint | Descripción |
|----------|-------------|
| `/api/v1/auth/login/` | Inicio de sesión (JWT) |
| `/api/v1/fincas/` | Gestión de fincas |
| `/api/v1/lotes/` | Gestión de lotes |
| `/api/v1/reports/agricultores/` | Reporte Excel de agricultores |
| `/api/v1/legal/terms/` | Términos y condiciones |
| `/api/v1/legal/privacy/` | Política de privacidad |

---

## 🧠 Autores

Proyecto desarrollado por aprendices de **Análisis y Desarrollo de Software (ADSO)** — Ficha 2923560, SENA Regional Guaviare

- 👨‍💻 **Camilo Andres Hernández Gonzales**
- 👨‍💻 **Jeferson Alexander Alvarez Rodríguez**
- 👨‍💻 **Cristian Camilo Camacho Morales**

---

## 🪪 Licencia

Este proyecto es de uso académico y no comercial, protegido bajo la licencia MIT.

© 2025 CacaoScan — Todos los derechos reservados.