#!/bin/sh
set -e

# Render inyecta PORT automáticamente, usar esa variable si está disponible
PORT=${PORT:-8080}

# Reemplazar el puerto en nginx.conf dinámicamente
sed -i "s/listen 8080;/listen ${PORT};/g" /etc/nginx/conf.d/default.conf

# Inyectar API_BASE_URL en runtime si está disponible
# Esto permite que la URL del API se configure dinámicamente sin rebuild
# Prioridad: RUNTIME_API_BASE_URL > VITE_API_BASE_URL (build-time)
API_URL="${RUNTIME_API_BASE_URL:-${VITE_API_BASE_URL:-}}"
if [ -n "${API_URL}" ]; then
    # Crear script de configuración que se carga antes de main.js
    CONFIG_SCRIPT="/usr/share/nginx/html/config.js"
    echo "window.__API_BASE_URL__ = '${API_URL}';" > "$CONFIG_SCRIPT"
    echo "✅ API Base URL configurada: ${API_URL}"
else
    # Crear script vacío para evitar 404
    CONFIG_SCRIPT="/usr/share/nginx/html/config.js"
    echo "// No runtime API URL configured" > "$CONFIG_SCRIPT"
fi

# Iniciar nginx
exec nginx -g 'daemon off;'

