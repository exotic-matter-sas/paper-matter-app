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

### Custom Paper Matter settings

You will need to rebuild the Docker image with the `docker/settings_local.py` customized.

### Logs

Execute `docker-compose logs -f` for all logs.
Execute `docker-compose logs -f [web|worker|redis|postgres]` for specific container logs.
