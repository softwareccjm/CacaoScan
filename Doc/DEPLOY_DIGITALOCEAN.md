# Deploy de CacaoScan en DigitalOcean Droplet

Guia paso a paso para levantar CacaoScan en un Droplet Basic de 2GB/1vCPU
con Caddy + Let's Encrypt y `docker-compose.prod.yml`.

## 1. Crear el Droplet

1. En DigitalOcean: **Create > Droplet**.
2. Imagen: **Ubuntu 24.04 LTS**.
3. Plan: **Basic > Regular > 2 GB / 1 vCPU / 50 GB** (~$12/mes).
4. Region: la mas cercana a tus usuarios.
5. Autenticacion: **SSH key** (no password). Sube tu clave publica.
6. Habilita **backups** ($2.4/mes, opcional pero recomendado).

## 2. Apuntar el dominio

En el panel de tu registrador (Namecheap, GoDaddy, etc.):

- Crea un registro **A**: `cacaoscan` -> `<IP del droplet>`.
- TTL: 300s (mientras pruebas; luego 3600s).
- Verifica con `dig +short cacaoscan.tudominio.com` desde tu maquina.

> Caddy emite el certificado TLS automaticamente la primera vez que el dominio
> resuelve al droplet. Hasta entonces sirve por HTTP.

## 3. Preparar el droplet

SSH al droplet (`ssh root@<ip>`) y dentro:

```bash
# Crear usuario no-root
adduser cacaoscan
usermod -aG sudo cacaoscan
rsync --archive --chown=cacaoscan:cacaoscan ~/.ssh /home/cacaoscan
# A partir de aqui, SSH como cacaoscan

# Firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Docker + Compose plugin
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Cierra y vuelve a abrir la sesion SSH para que tome el grupo

# Verificar
docker --version
docker compose version
```

## 4. Clonar el repo y configurar `.env`

```bash
cd ~
git clone https://github.com/JefersonCCJM/cacaoscan.git
cd cacaoscan

cp .env.production.example .env
nano .env
# Llena DOMAIN, LETSENCRYPT_EMAIL, SECRET_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD
```

Genera SECRET_KEY:

```bash
docker run --rm python:3.12-slim python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 5. Levantar la app

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

La primera vez tarda 5-10 min (compila imagen backend con PyTorch).

Verifica:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f backend
```

Espera a ver `Booting worker` de gunicorn. Luego prueba:

```bash
curl https://cacaoscan.tudominio.com/health
```

## 6. Despues del primer deploy

Edita `.env` y pon `SEED_INITIAL_DATA=false` (no necesitas reseedear en cada reinicio).
Reinicia solo el backend:

```bash
docker compose -f docker-compose.prod.yml up -d backend
```

## 7. Crear superuser

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## 8. Operacion diaria

| Tarea | Comando |
|---|---|
| Ver logs en vivo | `docker compose -f docker-compose.prod.yml logs -f backend` |
| Actualizar app (despues de `git pull`) | `docker compose -f docker-compose.prod.yml up -d --build` |
| Reiniciar todo | `docker compose -f docker-compose.prod.yml restart` |
| Shell Django | `docker compose -f docker-compose.prod.yml exec backend python manage.py shell` |
| Backup Postgres | `docker compose -f docker-compose.prod.yml exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%F).sql` |

## 9. Costos estimados

| Concepto | Mensual |
|---|---|
| Droplet 2GB/1vCPU | $12 |
| Backups automaticos (opcional) | $2.4 |
| **Total** | **~$14.4** |

Sin servicios externos: Postgres, Redis, backend, Celery worker, frontend y
Caddy corren en la misma maquina. Esta bien para tu volumen actual.

## 10. Que hacer si el droplet se queda corto

- **Subir a 4GB/2vCPU** ($24/mes): el cambio de plan se hace desde el
  Dashboard, requiere reinicio de unos minutos.
- **Mover Postgres a Managed Database** ($15/mes): mejor backups, alta
  disponibilidad, pero duplica el costo. Solo si manejas datos criticos.
- **Mover media files a Spaces** ($5/mes): si las imagenes de cacao crecen
  mucho, mueve `/srv/media` a DigitalOcean Spaces con django-storages.
