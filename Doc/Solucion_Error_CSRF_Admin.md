# Solución: Error CSRF 403 en Admin de Django

## Problema

Al intentar acceder al admin de Django, aparece el error:
```
Prohibido (403)
Verificación CSRF fallida. Solicitud abortada.
```

## Soluciones

### Solución 1: Verificar URL de Acceso

Asegúrate de acceder al admin usando una de estas URLs:
- `http://localhost:8000/admin/`
- `http://127.0.0.1:8000/admin/`

**NO uses**:
- `http://0.0.0.0:8000/admin/` ❌
- `http://192.168.x.x:8000/admin/` ❌ (a menos que esté en CSRF_TRUSTED_ORIGINS)

### Solución 2: Limpiar Cookies del Navegador

1. Abre las herramientas de desarrollador (F12)
2. Ve a la pestaña **Application** (Chrome) o **Storage** (Firefox)
3. En **Cookies**, elimina todas las cookies de `localhost` o `127.0.0.1`
4. Recarga la página

### Solución 3: Verificar Configuración en .env

Asegúrate de que tu archivo `.env` tenga:

```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### Solución 4: Reiniciar el Servidor

Después de cambiar la configuración:

1. Detén el servidor Django (Ctrl+C)
2. Reinicia el servidor:
```bash
python manage.py runserver
```

### Solución 5: Verificar que DEBUG=True

Si `DEBUG=False`, necesitas configurar explícitamente `CSRF_TRUSTED_ORIGINS`:

```env
DEBUG=False
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### Solución 6: Usar Modo Incógnito

Prueba acceder al admin en una ventana de incógnito para descartar problemas con cookies o extensiones del navegador.

### Solución 7: Verificar Middleware

Asegúrate de que el middleware CSRF esté activo en `settings.py`:

```python
MIDDLEWARE = [
    # ... otros middlewares ...
    'django.middleware.csrf.CsrfViewMiddleware',
    # ... otros middlewares ...
]
```

## Verificación

Para verificar que la configuración es correcta:

1. Accede a: `http://localhost:8000/api-info/`
2. Verifica que `csrf_trusted_origins` esté configurado correctamente

## Configuración Automática

El sistema ahora configura automáticamente `CSRF_TRUSTED_ORIGINS` en desarrollo con:
- `http://localhost:8000`
- `http://127.0.0.1:8000`
- `http://localhost:5173` (frontend)
- `http://127.0.0.1:5173` (frontend)

Si necesitas agregar más orígenes, configúralos en `.env`:

```env
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,https://tudominio.com
```

## Si el Problema Persiste

1. Verifica los logs del servidor Django para más detalles
2. Asegúrate de que no hay proxies o balanceadores de carga interfiriendo
3. Verifica que el puerto 8000 no esté siendo usado por otro proceso
4. Intenta acceder desde otro navegador

