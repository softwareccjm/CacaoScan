"""
URLs para autenticación JWT en CacaoScan.

Proporciona endpoints para login, logout, refresh de tokens
y gestión básica de usuarios con JWT.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

# Namespace para la app
app_name = 'auth'

urlpatterns = [
    # ==========================================
    # ENDPOINTS DE AUTENTICACIÓN JWT
    # ==========================================
    
    # Obtener par de tokens (access + refresh)
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Refrescar access token usando refresh token
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Verificar validez de un token
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Logout - blacklist del refresh token
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]

"""
Endpoints JWT implementados:

## POST /api/auth/login/
**Descripción**: Obtiene par de tokens JWT para usuario autenticado
**Body**:
```json
{
    "username": "usuario@example.com",
    "password": "contraseña123"
}
```
**Respuesta exitosa**:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## POST /api/auth/refresh/
**Descripción**: Obtiene nuevo access token usando refresh token
**Body**:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```
**Respuesta exitosa**:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## POST /api/auth/verify/
**Descripción**: Verifica si un token es válido
**Body**:
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```
**Respuesta exitosa**: `204 No Content`

## POST /api/auth/logout/
**Descripción**: Invalida refresh token (logout)
**Body**:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```
**Respuesta exitosa**: `204 No Content`

## Uso en Frontend:

### 1. Login:
```javascript
const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
});
const { access, refresh } = await response.json();
localStorage.setItem('access_token', access);
localStorage.setItem('refresh_token', refresh);
```

### 2. Uso del token:
```javascript
const response = await fetch('/api/images/', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
});
```

### 3. Refresh automático:
```javascript
const refreshToken = async () => {
    const refresh = localStorage.getItem('refresh_token');
    const response = await fetch('/api/auth/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh })
    });
    const { access } = await response.json();
    localStorage.setItem('access_token', access);
    return access;
};
```

### 4. Logout:
```javascript
const logout = async () => {
    const refresh = localStorage.getItem('refresh_token');
    await fetch('/api/auth/logout/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh })
    });
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
};
```
"""
