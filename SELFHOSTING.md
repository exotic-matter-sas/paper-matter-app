# Paper Matter (self hosting)

## Requirements

- Docker CE (latest LTS version)
- Docker-Compose (Compose file version 2)
- 1 vCPU, 1 GB RAM, 10 GB disk space (2 vCPU, 2 GB RAM recommended)

### Basic deployment (no ocr)

Copy the `docker-compose.sample.yml` to your directory of choice (don't forget to rename without `sample`).
The configured default should work out of the box but it's recommended to change some settings like `CRON_SECRET_KEY` and `DB_PASSWORD`.

Start the application with `docker-compose up -d`.

Database migration is not automatic. You need to execute a migration command inside the container running the web frontend
code.

Execute the following command to migrate database : `docker-compose exec web python3 manage.py migrate`.

Open your browser to http://localhost:8000 and follow instruction to create the super admin account.

### Backup

You should use the recommended Docker methods to backup the two volumes `dbdata` and `docs`.
https://docs.docker.com/storage/volumes/#backup-restore-or-migrate-data-volumes

### Available environment variable for Dockerfile

#### Database configuration
- DB_HOST = "postgres"
- DB_PORT = "5432"
- DB_NAME = "postgres"
- DB_USER = "postgres"
- DB_PASSWORD = "postgres"

#### Default Django storage backend
- DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

#### Google Cloud JSON Service Account Key
- GCS_CREDENTIALS_CONTENT = "CHANGEME"

#### Google Cloud Storage bucket name
- GCS_BUCKET_NAME = "CHANGEME"

#### Configuration for outbound email
- EMAIL_HOST = "CHANGEME"
- EMAIL_HOST_USER = "CHANGEME"
- EMAIL_HOST_PASSWORD = "CHANGEME"
- EMAIL_PORT = "25"
- DEFAULT_FROM_EMAIL = "noreply@localhost"

#### Redis server for Celery
- CELERY_REDIS_URL = "redis://redis:6379"

#### CRON secret key (part of the URL)
- CRON_SECRET_KEY = "CHANGEME"

#### Django secret key
- DJANGO_SECRET_KEY = "CHANGEME"

#### Use image as web frontend
- ENABLE_WEB = "true"

#### Use image as worker
- ENABLE_WORKER = "true"

#### Enable Django DEBUG mode
- DJANGO_DEBUG = "true"

#### Disable internal cron engine in Docker image
- CRON_DISABLE = "true"

#### Number of workers to fork
- NB_WORKERS = "1"

### Custom Paper Matter settings

You need to bind mount the local path `/app/ftl/settings_local.py`
and customize you own copy of the file `docker/settings_local.py`.

### Logs

Execute `docker-compose logs -f` for all logs.
Execute `docker-compose logs -f [web|worker|redis|postgres]` for specific container logs.
