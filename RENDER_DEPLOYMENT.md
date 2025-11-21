# 🚀 Guía de Despliegue en Render

Esta guía te ayudará a desplegar CacaoScan en Render (backend y frontend).

## 📋 Cambios Realizados

### 1. Backend (`backend/Dockerfile`)
- ✅ Ajustado para usar la variable `PORT` que Render inyecta automáticamente
- ✅ Gunicorn ahora escucha en el puerto dinámico

### 2. Frontend (`frontend/Dockerfile`)
- ✅ Creado script `start-nginx.sh` para ajustar el puerto de Nginx dinámicamente
- ✅ Dockerfile actualizado para usar el script de inicio

### 3. Configuración (`render.yaml`)
- ✅ Archivo de configuración declarativa para Render
- ✅ Define backend, frontend y base de datos PostgreSQL

---

## 🎯 Pasos para Desplegar

### Opción A: Usando render.yaml (Recomendado)

1. **Conecta tu repositorio a Render:**
   - Ve a [Render Dashboard](https://dashboard.render.com)
   - Click en "New" → "Blueprint"
   - Conecta tu repositorio de GitHub/GitLab
   - Render detectará automáticamente el archivo `render.yaml`

2. **Render creará automáticamente:**
   - ✅ Servicio web para el backend
   - ✅ Servicio web para el frontend
   - ✅ Base de datos PostgreSQL
   - ✅ Variables de entorno configuradas

3. **Configuraciones adicionales necesarias:**
   - En el servicio **backend**, agrega manualmente:
     ```
     ALLOWED_HOSTS=[nombre-del-backend].onrender.com
     ```
   - Verifica que `CORS_ALLOWED_ORIGINS` y `FRONTEND_URL` se hayan configurado automáticamente

4. **Espera a que el despliegue termine** (puede tomar 5-10 minutos la primera vez)

---

### Opción B: Despliegue Manual

#### Paso 1: Crear Base de Datos PostgreSQL

1. En Render Dashboard, click "New" → "PostgreSQL"
2. Configuración:
   - **Name:** `cacaoscan-db`
   - **Database:** `cacaoscan_db`
   - **User:** `cacaoscan_user`
   - **Plan:** Starter (o superior para producción)
3. Guarda y anota las credenciales

#### Paso 2: Desplegar Backend

1. Click "New" → "Web Service"
2. Conecta tu repositorio
3. Configuración:
   - **Name:** `cacaoscan-backend`
   - **Region:** Elige la más cercana
   - **Branch:** `main` (o tu rama principal)
   - **Root Directory:** `backend`
   - **Runtime:** Docker
   - **Dockerfile Path:** `Dockerfile`
   - **Docker Context:** `backend`
   - **Build Command:** (dejar vacío)
   - **Start Command:** (dejar vacío)
4. **Environment Variables:**
   ```
   DEBUG=False
   SECRET_KEY=[genera una clave segura - Render puede generarla automáticamente]
   DB_NAME=[del servicio PostgreSQL]
   DB_USER=[del servicio PostgreSQL]
   DB_PASSWORD=[del servicio PostgreSQL]
   DB_HOST=[del servicio PostgreSQL]
   DB_PORT=5432
   ALLOWED_HOSTS=[nombre-del-backend].onrender.com
   CREATE_DEFAULT_SUPERUSER=true
   SEED_INITIAL_DATA=true
   ```
5. **Advanced Settings:**
   - Health Check Path: `/health`
6. Click "Create Web Service"

#### Paso 3: Desplegar Frontend

1. Click "New" → "Web Service"
2. Conecta el mismo repositorio
3. Configuración:
   - **Name:** `cacaoscan-frontend`
   - **Region:** La misma que el backend
   - **Branch:** `main`
   - **Root Directory:** `frontend`
   - **Runtime:** Docker
   - **Dockerfile Path:** `Dockerfile`
   - **Docker Context:** `frontend`
   - **Build Command:** (dejar vacío)
   - **Start Command:** (dejar vacío)
4. **Environment Variables:**
   ```
   VITE_API_BASE_URL=https://[nombre-del-backend].onrender.com/api/v1
   ```
   ⚠️ **IMPORTANTE:** Esta variable se usa en **build time**, no runtime. Si cambias la URL del backend después, necesitarás reconstruir el frontend.
5. **Advanced Settings:**
   - Health Check Path: `/health`
6. Click "Create Web Service"

#### Paso 4: Configurar CORS en Backend

1. Ve al servicio del backend
2. En "Environment", agrega:
   ```
   CORS_ALLOWED_ORIGINS=https://[nombre-del-frontend].onrender.com
   FRONTEND_URL=https://[nombre-del-frontend].onrender.com
   ```
3. Guarda los cambios (esto reiniciará el servicio)

---

## ✅ Verificación

Una vez desplegado, verifica:

1. **Backend Health Check:**
   ```
   https://[nombre-backend].onrender.com/health
   ```
   Debe devolver: `{"status": "ok", "service": "cacaoscan-backend"}`

2. **Frontend:**
   ```
   https://[nombre-frontend].onrender.com
   ```
   Debe mostrar la aplicación Vue

3. **API Endpoint:**
   ```
   https://[nombre-backend].onrender.com/api/v1/
   ```

---

## 🔧 Variables de Entorno Importantes

### Backend
- `PORT` - Render lo inyecta automáticamente (no configurar manualmente)
- `SECRET_KEY` - Clave secreta de Django (Render puede generarla)
- `DEBUG` - Debe ser `False` en producción
- `ALLOWED_HOSTS` - Dominio del backend en Render
- `CORS_ALLOWED_ORIGINS` - URL del frontend
- Variables de base de datos (se configuran automáticamente si usas `render.yaml`)

### Frontend
- `VITE_API_BASE_URL` - URL completa del backend API (incluye `/api/v1`)
- `PORT` - Render lo inyecta automáticamente (no configurar manualmente)

---

## 🐛 Solución de Problemas

### El backend no inicia
- Verifica que las variables de base de datos estén correctas
- Revisa los logs en Render Dashboard
- Asegúrate de que `ALLOWED_HOSTS` incluya el dominio de Render

### El frontend no se conecta al backend
- Verifica que `VITE_API_BASE_URL` esté correctamente configurada
- Asegúrate de que `CORS_ALLOWED_ORIGINS` en el backend incluya la URL del frontend
- Reconstruye el frontend si cambiaste la URL del backend

### Error 502 Bad Gateway
- Espera unos minutos (el despliegue puede tardar)
- Verifica los health checks
- Revisa los logs del servicio

### Migraciones no se ejecutan
- El `docker-entrypoint.sh` ejecuta migraciones automáticamente
- Si hay problemas, puedes ejecutarlas manualmente desde el shell de Render

---

## 📝 Notas Importantes

1. **Primer despliegue:** Puede tardar 10-15 minutos debido a la instalación de dependencias ML (PyTorch, etc.)

2. **Planes de Render:**
   - **Starter:** Gratis, pero con limitaciones (sleep después de inactividad)
   - **Standard/Pro:** Recomendado para producción, sin sleep

3. **Base de datos:**
   - Las migraciones se ejecutan automáticamente
   - El superusuario se crea automáticamente si `CREATE_DEFAULT_SUPERUSER=true`
   - Los catálogos se inicializan si `SEED_INITIAL_DATA=true`

4. **Archivos estáticos y media:**
   - Los estáticos se sirven con WhiteNoise
   - Los archivos media se guardan localmente (considera usar S3 para producción)

5. **Variables de entorno sensibles:**
   - `SECRET_KEY` debe ser única y segura
   - Las credenciales de base de datos se manejan automáticamente con `render.yaml`

---

## 🔄 Actualizaciones Futuras

Para actualizar el despliegue:
1. Haz push a tu rama principal
2. Render detectará los cambios automáticamente
3. Reconstruirá y redesplegará los servicios

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Render Dashboard
2. Verifica las variables de entorno
3. Asegúrate de que los health checks estén funcionando

¡Listo para desplegar! 🚀

