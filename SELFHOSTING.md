# Paper Matter (self hosting)

## Requirements

- Docker CE (latest LTS version)
- Docker-Compose (Compose file version 2)
- 1 vCPU, 1 GB RAM, 10 GB disk space (2 vCPU, 2 GB RAM recommended)

### Basic deployment (for test purpose)

__This deployment should be only considered as a first step, it will use default settings and is **NOT SECURE** for production use.__

1. Copy the `docker-compose.sample.yml` to your directory of choice (don't forget to rename without `sample`).

2. Start the application:

    `docker-compose up -d`

3. Then to setup the database, you need to execute a migration command inside the container running the web frontend
code. Execute the following command to migrate database: 

    `docker-compose exec web python3 manage.py migrate`

4. Open your browser to http://localhost:8000 and follow instruction to create the super admin account.

### Secured deployment (for production use)

__Complete the steps described in **Basic deployment** section first.__

1. Stop the application:

    `docker-compose down`

2. Update security keys settings in `docker-compose.yml`:

| Name | Default value | Format | Description |
| --- | --- | --- | --- |
| DJANGO_SECRET_KEY | `CHANGE-ME` | Randomly generated string (at least 50 characters long) | It is use by Django for cryptographic signing, [more infos](https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-SECRET_KEY) |
| CRON_SECRET_KEY | `change-me` | Randomly generated string with ONLY url friendly characters (eg: unaccented characters [a-z], number [0-9], and hyphen [-_]. At least 50 characters long) | It is used by PM to restrict access to URL allowing to run periodic tasks |

3. Update database settings in `docker-compose.yml`:

| Name | Default value | Description |
| --- | --- | --- |
| DB_NAME | `postgres` | Name of the PostgreSQL database used Django, you have to [update the DB name accordingly](https://www.postgresql.org/docs/11/sql-alterdatabase.html)|
| DB_USER | `postgres` | User used by Django to access the PostgreSQL database, you have to [update the DB access accordingly](https://www.postgresql.org/docs/11/sql-alteruser.html) |
| DB_PASSWORD | `postgres` | Password used by Django to access the PostgreSQL database, you have to [update the DB access accordingly](https://www.postgresql.org/docs/11/sql-alteruser.html) |
| DB_HOST | `postgres` | Host name / ip of the PostgreSQL server used by Django, you can safely let the default value for this setting|
| DB_PORT | `5432` | Port of the PostgreSQL server used by Django, you can safely let the default value for this setting|

4. Update outbound email server settings in `docker-compose.yml`:

__Email server is not included in the Docker but it is required to send activation email to user signing up to your Paper Matter instance (and for other features like forgot password).__

| Name | Default value | Description 
| --- | --- | --- |
| EMAIL_HOST | `CHANGE-ME` | Host name / ip of the email server used by Django, we recommend you to subscribe to an transactional email provider |
| EMAIL_HOST_USER | `CHANGE-ME` | User used by Django to access the email server |
| EMAIL_HOST_PASSWORD | `CHANGE-ME` | Password used by Django to access the email server |
| EMAIL_PORT | `25` | Port used by Django to access the email server |
| DEFAULT_FROM_EMAIL | `noreply@localhost` | This is sender which will appears in the email received by your PM instance users |

5. (optional) Additional settings

| Name | Default value | Format | Description |
| --- | --- | --- | --- |
| ALLOWED_HOSTS | `*` | A comma separated list of hosts url (eg. `mypminstance.com, my-pm-instance.com`) |It improve security by defining the host allowed to serve your PM instance, [more infos](https://docs.djangoproject.com/en/3.0/ref/settings/#allowed-hosts) |

6. Start the application:

    `docker-compose up -d`

### Backup

You should use the recommended Docker methods to backup the two volumes `dbdata` and `docs`.
https://docs.docker.com/storage/volumes/#backup-restore-or-migrate-data-volumes

### Customize the file storage

__By default the documents binaries are stored using the file system into the `uploads` folder, if you want you can set the ENV `DEFAULT_FILE_STORAGE` to use [Amazon S3](https://aws.amazon.com/s3/) or [Google cloud Storage](https://cloud.google.com/storage).__

#### Amazon S3 settings

Set `DEFAULT_FILE_STORAGE` to `storages.backends.s3boto3.S3Boto3Storage` and set the additional settings bellow:

| Name | Description |
| --- | --- |
| AWS_ACCESS_KEY_ID | - |
| AWS_SECRET_ACCESS_KEY | - |
| AWS_STORAGE_BUCKET_NAME | - |
| AWS_S3_ENDPOINT_URL | - |
| AWS_S3_REGION_NAME | - |

#### Google Cloud Storage settings

Set `DEFAULT_FILE_STORAGE` to `storages.backends.gcloud.GoogleCloudStorage` and set the additional settings bellow:

| Name | Format | Description |
| --- | --- | --- |
| GCS_BUCKET_NAME | - | - |
| GCS_CREDENTIALS_CONTENT | JSON, see example bellow  | - |

`GCS_CREDENTIALS_CONTENT` example:

```JSON
{
    "type": "service_account",
    "project_id": "CHANGE-ME",
    "private_key_id": "CHANGE-ME",
    "private_key": "CHANGE-ME",
    "client_email": "CHANGE-ME",
    "client_id": "CHANGE-ME",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "CHANGE-ME"
}
```

### Enable the OCR feature

__By default the OCR feature is disabled, it allow to search for keywords inside scanned documents.__

You can't enable OCR feature using ENV variables for now, but you can do it as described in `Customize Paper Matter other settings` bellow.

### Various other settings that you can update with ENV

| Name | Default value | Format | Description |
| --- | --- | --- | --- |
| DJANGO_DEBUG | `False` | `True` or `False` | Enable Django DEBUG mode, DO NOT enable this mode on if your instance is used in production, [more infos](https://docs.djangoproject.com/en/3.0/ref/settings/#debug) |
| CRON_DISABLE | `False` | `True` or `False` | Disable internal cron engine in Docker image |
| NB_WORKERS | `1`  | A number >= 1 | Number of workers which will run documents processing in parallel, increasing this number can impact significantly server load (to use on an image with `ENABLE_WORKER` set to `true`) |

### Customize Paper Matter other settings

You need to [bind mount](https://docs.docker.com/storage/bind-mounts/) the local path `/app/ftl/settings_local.py` and customize you own copy of the file `docker/settings_local.py`.

### Logs

Execute `docker-compose logs -f` for all logs.
Execute `docker-compose logs -f [web|worker|redis|postgres]` for specific container logs.
