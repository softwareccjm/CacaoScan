# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Screenshots

Cuando el usuario mencione una captura de pantalla (sin dar ruta), búscala en `C:\Users\jefer\OneDrive\Pictures\Screenshots` — toma la más reciente por defecto.

## Project Overview

CacaoScan is a full-stack platform that measures dimensions and weight of cacao beans using computer vision and ML. It pairs a Django REST API (PyTorch + YOLOv8 + scikit-learn) with a Vue 3 SPA. The backend serves the API and admin; the frontend is the user-facing UI.

## Common Commands

### Top-level (Docker / Make)
- `make up` / `docker compose up -d --build` — full stack (backend, frontend, postgres, redis)
- `make down`, `make logs`, `make clean` (clean removes volumes — destroys DB)
- `make test` — runs backend pytest + frontend vitest
- `make deploy` / `make k8s-status` / `make k8s-logs` — Kubernetes via `k8s/`

### Backend (`cd backend`, requires Python 3.12 exactly)
- Create venv: `py -3.12 -m venv venv && venv\Scripts\activate` (Windows) or `source venv/bin/activate`
- Install: `pip install -r requirements.txt`
- Run: `python manage.py runserver` → http://127.0.0.1:8000
- Migrations: `python manage.py makemigrations && python manage.py migrate`
- Seeders (required after fresh DB): `python manage.py init_catalogos` then `python manage.py seed_colombia`
- Tests: `pytest` (config in `backend/pytest.ini`, uses `--reuse-db --nomigrations`)
- Single test: `pytest api/tests/test_foo.py::TestClass::test_method`
- Parallel: `pytest -n auto` (pytest-xdist installed)
- Coverage: `pytest --cov`
- Inside Docker: `docker compose exec backend python manage.py <cmd>`

### Frontend (`cd frontend`, requires Node `^20.19.0 || >=22.12.0`, prefer pnpm)
- Install: `pnpm install`
- Dev: `pnpm dev` → http://127.0.0.1:5173
- Build / preview: `pnpm build` / `pnpm preview`
- Tests: `pnpm test` (vitest watch), `pnpm test:unit` (single run + coverage)
- Lint / format: `pnpm lint`, `pnpm format`

### ML Pipeline (run inside backend container, in order)
1. `python manage.py train_unet_background --epochs 20 --batch-size 16` — produces `ml/segmentation/cacao_unet.pth`
2. `python manage.py calibrate_dataset_pixels --segmentation-backend auto` — produces crops + `media/datasets/pixel_calibration.json`
3. `python manage.py train_cacao_models --hybrid --use-pixel-features --epochs 50 --batch-size 32` — produces `ml/artifacts/regressors/hybrid.pt`

GPU is auto-detected; lower batch sizes (4–8) when on CPU. Source data goes in `backend/media/cacao_images/raw/` and `backend/media/datasets/`.

## Architecture

### Backend layout (`backend/`)
Django project is `cacaoscan/` (settings, urls, asgi/wsgi). Apps are mounted under `/api/v1/` from `cacaoscan/urls.py`:
- `api/` — primary REST surface; contains `views/`, `serializers/`, `services/`, `tasks/`, plus realtime infra (`consumers.py`, `routing.py`, `realtime_service.py`, `realtime_middleware.py`, `cache_config.py`). Most cross-cutting endpoints live here.
- `auth_app/` — JWT auth (SimpleJWT) and login endpoints.
- `personas/` — user/agricultor/técnico profiles. Mounted *before* `api.urls` to avoid prefix conflicts.
- `fincas_app/` — fincas (farms) and lotes (lots).
- `images_app/` — image upload/storage and dataset ingestion (S3-capable via django-storages).
- `catalogos/` — reference data (countries, regions, cacao varieties); seeded by management commands.
- `reports/` — Excel/PDF report generation (openpyxl, XlsxWriter, reportlab).
- `notifications/`, `audit/` — notification delivery and audit log.
- `legal/` — terms and privacy endpoints.
- `training/` — ML training orchestration (management commands and services for the pipeline above).
- `ml/` — model code organized by stage: `segmentation/`, `classification/`, `regression/`, `prediction/`, `measurement/`, `pipeline/`, plus `artifacts/` for trained weights.
- `core/`, `users/` — shared models and primitives.

URL loading is defensive: each app's URLconf is wrapped in try/except so a broken app doesn't take down the whole API. When adding routes, follow the *specific-before-general* ordering already in `cacaoscan/urls.py`.

Realtime: `channels` + `channels_redis` provide WebSockets via `api/routing.py` and `api/consumers.py`. Async tasks use Celery (worker + beat services in `docker-compose.yml`); broker/cache is Redis. Celery only starts in containers when `USE_CELERY_REDIS` is enabled and `CELERY_BROKER_URL` is set (see `docker-entrypoint.sh`).

Settings (`cacaoscan/settings.py`) auto-generates a dev `.env` if missing (only when `APP_ENV != production`) and force-sanitizes `.env` bytes (BOM/latin-1) before loading. Production requires `.env` to exist or it raises. `env.example` is the reference.

### Frontend layout (`frontend/src/`)
Standard Vue 3 SPA: `views/` (route pages), `components/` (reusable), `stores/` (Pinia), `router/`, `services/` (axios API clients), `composables/`, `utils/`, `assets/`, `styles/`. Tailwind v4 via `@tailwindcss/vite`. API base URL comes from `VITE_API_BASE_URL`. Tests live in `__tests__/` and `src/test/` and run under vitest + jsdom.

### Deployment
- `docker-compose.yml` (root) wires backend, frontend (nginx), db (postgres 15), redis, celery worker, celery beat.
- `render.yaml` + `RENDER_ENVIRONMENT_VARIABLES.md` define Render deployment; `Doc/` has guides for AWS S3 and CSRF troubleshooting.
- `k8s/` contains Kustomize manifests; namespace defaults to `app-namespace` (override with `K8S_NS=...`).
- Sonar config in `sonar-project.properties`; `run_sonar_full.bat` runs full analysis.

## Repo-Specific Gotchas

- **Python 3.12 only.** 3.11 and 3.13 break (the settings file even shims `SecurityWarning` for 3.12).
- **`pytest.ini` ignores many test files** that currently fail due to schema/factory drift. Don't assume an `--ignore`d test is supposed to pass; check before "fixing" by un-ignoring.
- **Comment hygiene (from global CLAUDE.md):** when editing any file, audit existing comments — delete obvious/stale ones, fix wrong ones. Keep comments sparse, accurate, and useful.
- **Two `docker-compose.yml` files** exist (root and `backend/`). The root one is the source of truth for full-stack dev; the backend-local one is for backend-only workflows.
- **URL prefixes:** all v1 routes go under `/api/v1/`. `personas/` is mounted before `api/` deliberately — preserve that order when adding apps.
- **Spanish-language project.** Code identifiers, commit messages, docs, and user-facing strings are in Spanish. Match this when writing new code or docs.
