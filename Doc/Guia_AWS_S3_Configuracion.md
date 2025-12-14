# Guía de Configuración de AWS S3 para CacaoScan

Esta guía te ayudará a configurar AWS S3 para almacenar las imágenes de análisis en la nube.

## Requisitos Previos

- Una cuenta de AWS (puedes crear una en https://aws.amazon.com/)
- Acceso a la consola de AWS

## Paso 1: Crear un Bucket S3

1. Inicia sesión en la [Consola de AWS](https://console.aws.amazon.com/)
2. Navega a [S3](https://console.aws.amazon.com/s3/)
3. Haz clic en **"Create bucket"** (Crear bucket)
4. Configura el bucket:
   - **Bucket name**: `cacaoscan-dataset` (o el nombre que prefieras)
   - **AWS Region**: `us-east-1` (o la región más cercana a ti)
   - Deja las demás opciones por defecto
5. Haz clic en **"Create bucket"**

## Paso 2: Crear un Usuario IAM

1. Navega a [IAM](https://console.aws.amazon.com/iam/)
2. En el menú lateral, haz clic en **"Users"** (Usuarios)
3. Haz clic en **"Create user"** (Crear usuario)
4. Configura el usuario:
   - **User name**: `cacaoscan-s3-user` (o el nombre que prefieras)
   - Selecciona **"Access key - Programmatic access"** (Acceso mediante clave de acceso)
5. Haz clic en **"Next"**

## Paso 3: Asignar Permisos S3

Tienes dos opciones:

### Opción A: Política Completa (Recomendado para desarrollo)

1. Selecciona **"Attach policies directly"**
2. Busca y selecciona **"AmazonS3FullAccess"**
3. Haz clic en **"Next"** y luego **"Create user"**

### Opción B: Política Personalizada (Recomendado para producción)

1. Selecciona **"Attach policies directly"**
2. Haz clic en **"Create policy"**
3. En la pestaña **"JSON"**, pega esta política:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::cacaoscan-dataset",
                "arn:aws:s3:::cacaoscan-dataset/*"
            ]
        }
    ]
}
```

**Nota**: Reemplaza `cacaoscan-dataset` con el nombre de tu bucket.

4. Nombra la política: `CacaoScanS3Access`
5. Haz clic en **"Create policy"**
6. Vuelve a la creación del usuario y selecciona la política que acabas de crear
7. Haz clic en **"Next"** y luego **"Create user"**

## Paso 4: Generar Access Keys

1. Una vez creado el usuario, haz clic en su nombre
2. Ve a la pestaña **"Security credentials"** (Credenciales de seguridad)
3. En la sección **"Access keys"**, haz clic en **"Create access key"**
4. Selecciona **"Application running outside AWS"** (Aplicación fuera de AWS)
5. Haz clic en **"Next"** y luego **"Create access key"**
6. **IMPORTANTE**: Copia inmediatamente:
   - **Access key ID**: Ejemplo: `AKIAIOSFODNN7EXAMPLE`
   - **Secret access key**: Ejemplo: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
   
   ⚠️ **ADVERTENCIA**: La Secret Access Key solo se muestra UNA VEZ. Si la pierdes, tendrás que crear una nueva.

## Paso 5: Configurar en CacaoScan

1. Abre el archivo `.env` en la raíz del proyecto `backend/`
2. Configura las siguientes variables:

```env
USE_S3=True
AWS_ACCESS_KEY_ID=tu_access_key_id_aqui
AWS_SECRET_ACCESS_KEY=tu_secret_access_key_aqui
AWS_STORAGE_BUCKET_NAME=cacaoscan-dataset
AWS_S3_REGION_NAME=us-east-1
```

3. Reemplaza los valores con tus credenciales reales

## Paso 6: Verificar la Configuración

1. Reinicia el servidor Django
2. Sube una imagen de análisis
3. Verifica en la consola de S3 que la imagen se haya guardado en el bucket

## Seguridad

### Buenas Prácticas

1. **Nunca subas el archivo `.env` al repositorio** (ya está en `.gitignore`)
2. **No compartas tus credenciales** con nadie
3. **Usa políticas de acceso mínimo** en producción (Opción B del Paso 3)
4. **Rota las credenciales periódicamente** (cada 90 días recomendado)
5. **Habilita MFA** en tu cuenta de AWS principal

### Si Comprometes tus Credenciales

1. Ve a IAM > Users > Tu usuario
2. Security credentials > Access keys
3. Haz clic en "Delete" en la clave comprometida
4. Crea una nueva clave de acceso
5. Actualiza el archivo `.env` con las nuevas credenciales

## Costos

AWS S3 tiene un modelo de pago por uso:
- **Almacenamiento**: ~$0.023 por GB/mes (primeros 50 TB)
- **Transferencia de datos**: Gratis para los primeros 100 GB/mes
- **Requests**: Muy económicos (miles de requests por centavos)

Para un proyecto pequeño, los costos suelen ser menores a $1 USD/mes.

## Solución de Problemas

### Error: "Access Denied"
- Verifica que el usuario IAM tenga los permisos correctos
- Verifica que el nombre del bucket sea correcto
- Verifica que las credenciales estén correctas en el `.env`

### Error: "Bucket does not exist"
- Verifica que el bucket esté creado en la región correcta
- Verifica que `AWS_STORAGE_BUCKET_NAME` coincida con el nombre del bucket

### Error: "Invalid credentials"
- Verifica que copiaste correctamente el Access Key ID y Secret Access Key
- Asegúrate de que no haya espacios extra en el `.env`
- Verifica que `USE_S3=True` esté configurado

## Recursos Adicionales

- [Documentación oficial de AWS S3](https://docs.aws.amazon.com/s3/)
- [Documentación de IAM](https://docs.aws.amazon.com/iam/)
- [Calculadora de precios de S3](https://calculator.aws/)

