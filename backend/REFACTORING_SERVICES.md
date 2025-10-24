# Refactorización a Capa de Servicios - CacaoScan

## Resumen

Se ha completado la refactorización de las vistas de CacaoScan para usar una arquitectura de capa de servicios. Esto mejora la separación de responsabilidades, hace el código más mantenible y facilita las pruebas.

## Estructura de Servicios

### Archivos Creados

```
backend/api/services/
├── __init__.py              # Exportaciones y instancias de servicios
├── base.py                  # Clases base y utilidades comunes
├── auth_service.py          # Servicio de autenticación
├── analysis_service.py      # Servicio de análisis de granos
├── image_service.py         # Servicio de gestión de imágenes
├── finca_service.py        # Servicios de fincas y lotes
└── report_service.py       # Servicio de reportes
```

### Archivos Refactorizados

```
backend/api/
├── refactored_views.py      # Vistas refactorizadas usando servicios
└── views.py                # Vistas originales (mantenidas para compatibilidad)
```

## Servicios Implementados

### 1. AuthenticationService (`auth_service.py`)

**Funcionalidades:**
- Login de usuarios con tokens JWT
- Registro de nuevos usuarios
- Logout y invalidación de tokens
- Verificación de email
- Restablecimiento de contraseña
- Gestión de perfiles de usuario

**Métodos principales:**
```python
auth_service.login_user(username, password, request)
auth_service.register_user(user_data, request)
auth_service.logout_user(user, refresh_token)
auth_service.verify_email(token)
auth_service.forgot_password(email, request)
auth_service.reset_password(token, new_password, confirm_password)
auth_service.get_user_profile(user)
auth_service.update_user_profile(user, profile_data)
```

### 2. AnalysisService (`analysis_service.py`)

**Funcionalidades:**
- Análisis de granos de cacao desde imágenes
- Historial de análisis con paginación y filtros
- Detalles de análisis específicos
- Eliminación de análisis
- Estadísticas de análisis

**Métodos principales:**
```python
analysis_service.analyze_cacao_grain(image_file, user)
analysis_service.get_analysis_history(user, page, page_size, filters)
analysis_service.get_analysis_details(analysis_id, user)
analysis_service.delete_analysis(analysis_id, user)
analysis_service.get_analysis_statistics(user, filters)
```

### 3. ImageManagementService (`image_service.py`)

**Funcionalidades:**
- Subida de imágenes
- Gestión de metadatos
- Historial de imágenes con filtros
- Eliminación de imágenes
- Estadísticas de imágenes

**Métodos principales:**
```python
image_service.upload_image(image_file, user, metadata)
image_service.get_user_images(user, page, page_size, filters)
image_service.get_image_details(image_id, user)
image_service.update_image_metadata(image_id, user, metadata)
image_service.delete_image(image_id, user)
image_service.get_image_statistics(user, filters)
```

### 4. FincaService y LoteService (`finca_service.py`)

**FincaService:**
- Creación y gestión de fincas
- Listado con filtros y paginación
- Actualización y eliminación
- Estadísticas de fincas

**LoteService:**
- Creación y gestión de lotes
- Lotes por finca
- Actualización y eliminación
- Estadísticas de lotes

**Métodos principales:**
```python
# Fincas
finca_service.create_finca(finca_data, user)
finca_service.get_user_fincas(user, page, page_size, filters)
finca_service.get_finca_details(finca_id, user)
finca_service.update_finca(finca_id, user, finca_data)
finca_service.delete_finca(finca_id, user)

# Lotes
lote_service.create_lote(lote_data, user)
lote_service.get_finca_lotes(finca_id, user, page, page_size, filters)
lote_service.get_lote_details(lote_id, user)
lote_service.update_lote(lote_id, user, lote_data)
lote_service.delete_lote(lote_id, user)
```

### 5. ReportService (`report_service.py`)

**Funcionalidades:**
- Generación de reportes de análisis
- Reportes por finca y lote
- Historial de reportes
- Estadísticas de reportes

**Métodos principales:**
```python
report_service.generate_analysis_report(user, report_data)
report_service.get_user_reports(user, page, page_size, filters)
report_service.get_report_details(report_id, user)
report_service.delete_report(report_id, user)
report_service.get_report_statistics(user, filters)
```

## Clases Base

### BaseService

Clase base que proporciona funcionalidades comunes:

- **Logging:** Métodos para log_info, log_warning, log_error
- **Validación:** validate_required_fields, validate_field_values
- **Permisos:** validate_user_permission, check_user_permission
- **Transacciones:** execute_with_transaction
- **Paginación:** paginate_results
- **Auditoría:** create_audit_log

### ServiceResult

Clase para encapsular resultados de servicios:

```python
# Resultado exitoso
result = ServiceResult.success(data=response_data, message="Operación exitosa")

# Resultado de error
result = ServiceResult.error(ValidationServiceError("Error de validación"))

# Resultados específicos
result = ServiceResult.validation_error("Campo requerido faltante")
result = ServiceResult.permission_error("Sin permisos")
result = ServiceResult.not_found_error("Recurso no encontrado")
```

### Excepciones de Servicio

- **ServiceError:** Excepción base
- **ValidationServiceError:** Errores de validación
- **PermissionServiceError:** Errores de permisos
- **NotFoundServiceError:** Recurso no encontrado

## Vistas Refactorizadas

### Ejemplo de Uso en Vistas

```python
from .services import auth_service, analysis_service

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return create_error_response(
                message="Datos de login inválidos",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar servicio
        result = auth_service.login_user(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
            request=request
        )
        
        if result.success:
            return create_success_response(
                data=result.data,
                message=result.message,
                status_code=status.HTTP_200_OK
            )
        else:
            return create_error_response(
                message=result.error.message,
                errors=result.error.details,
                status_code=status.HTTP_401_UNAUTHORIZED
            )
```

## Beneficios de la Refactorización

### 1. **Separación de Responsabilidades**
- Las vistas solo manejan HTTP y serialización
- La lógica de negocio está en los servicios
- Validaciones centralizadas en servicios

### 2. **Reutilización de Código**
- Los servicios pueden ser usados desde múltiples vistas
- Lógica común en BaseService
- Instancias de servicios disponibles globalmente

### 3. **Facilidad de Pruebas**
- Servicios pueden ser probados independientemente
- Mocking más sencillo
- Tests unitarios más enfocados

### 4. **Mantenibilidad**
- Código más organizado y estructurado
- Cambios en lógica de negocio no afectan vistas
- Debugging más fácil

### 5. **Consistencia**
- Manejo uniforme de errores
- Respuestas estandarizadas
- Logging consistente

## Migración Gradual

### Estrategia de Implementación

1. **Fase 1:** Servicios creados y probados ✅
2. **Fase 2:** Vistas refactorizadas creadas ✅
3. **Fase 3:** Actualizar URLs para usar vistas refactorizadas
4. **Fase 4:** Tests para servicios
5. **Fase 5:** Deprecar vistas antiguas

### Actualización de URLs

Para usar las vistas refactorizadas, actualizar `urls.py`:

```python
# Antes
from .views import LoginView, RegisterView, ScanMeasureView

# Después
from .refactored_views import LoginView, RegisterView, ScanMeasureView
```

## Testing de Servicios

### Ejemplo de Test

```python
from django.test import TestCase
from django.contrib.auth.models import User
from api.services import auth_service

class AuthenticationServiceTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
    
    def test_register_user_success(self):
        result = auth_service.register_user(self.user_data)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data['access'])
        self.assertIsNotNone(result.data['refresh'])
        self.assertEqual(result.message, "Usuario registrado exitosamente")
    
    def test_register_user_duplicate_email(self):
        # Crear usuario existente
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='pass123'
        )
        
        result = auth_service.register_user(self.user_data)
        
        self.assertFalse(result.success)
        self.assertEqual(result.error.message, "Este email ya está registrado")
```

## Próximos Pasos

1. **Completar Tests:** Crear tests unitarios para todos los servicios
2. **Documentación API:** Actualizar documentación Swagger
3. **Migración URLs:** Cambiar URLs para usar vistas refactorizadas
4. **Monitoreo:** Implementar métricas de servicios
5. **Cache:** Agregar cache a servicios que lo requieran

## Conclusión

La refactorización a capa de servicios ha mejorado significativamente la arquitectura del código de CacaoScan. Los servicios proporcionan una interfaz limpia y consistente para la lógica de negocio, facilitando el mantenimiento, testing y escalabilidad del sistema.

La implementación mantiene compatibilidad con el código existente mientras proporciona una base sólida para futuras mejoras y funcionalidades.
