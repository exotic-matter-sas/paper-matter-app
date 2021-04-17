FROM node:lts-alpine AS frontdependencies
ADD /ftl/frontend/package*.json /app/
WORKDIR /app
RUN npm ci



FROM frontdependencies AS frontbuild
COPY /ftl/frontend /app
WORKDIR /app
RUN npm run build



FROM python:3.7-slim AS compile-image
# mkdir Workaround for https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=863199
RUN mkdir -p /usr/share/man/man1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext \
    openjdk-11-jre-headless \
    build-essential \
    python3-dev \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    supervisor \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

ADD ftl/requirements.txt /app/requirements.txt
ADD docker/app/requirements_deploy.txt /app/requirements_deploy.txt


RUN python -m venv /opt/venv
# Activate venv
ENV PATH="/opt/venv/bin:$PATH"

RUN python3 -m pip install -r /app/requirements.txt --no-cache-dir && \
 python3 -m pip install -r /app/requirements_deploy.txt --no-cache-dir



FROM python:3.7-slim AS build-image
# Configure the listening PORT for the web frontend server (used by uwsgi)
ENV PORT 8000
# Set to "true" to use this image as a web frontend
ENV ENABLE_WEB false
# Set to "true" to use this image as a task scheduler (cron)
ENV ENABLE_CRON false
# Set to "true" to use this image as a worker
ENV ENABLE_WORKER false
# Set number of workers for async processing such as OCR
ENV NB_WORKERS 1
# Celery queue configuration (indicate which queue should the worker(s) work(s) on
ENV WORKER_QUEUES ftl_processing,med,celery
# Set time limit in seconds for each job in async processing (child process will be force restart)
ENV JOB_TIMELIMIT 900
# Directory for documents binary
ENV FTLDATA /app/uploads

# WARNING: NOT SECURE FOR PRODUCTION
# ===================================
# For production use, additional ENV variables have to be defined to update default security settings.
# The recommanded way to set theses variables is to set them at runtime (either via docker command or via your
# deployment method). Refer to SELFHOSTING.MD for the list of ENV available.

# mkdir workaround for https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=863199
RUN mkdir -p /usr/share/man/man1 \
    && mkdir -p "$FTLDATA" \
    && chmod 700 "$FTLDATA"

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless \
    supervisor \
    gettext \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=compile-image /opt/venv /opt/venv
COPY docker/ /
COPY ftl /app/
COPY --from=frontbuild /app/dist /app/frontend/dist
COPY --from=frontbuild /app/pdfjs /app/frontend/pdfjs
COPY --from=frontbuild /app/webpack-stats.json /app/frontend/
COPY --from=frontbuild /app/__init__.py /app/frontend/

WORKDIR /app

# Activate venv
ENV PATH="/opt/venv/bin:$PATH"

RUN python3 -m compileall ./ \
    && python3 manage.py compilemessages \
    && python3 manage.py collectstatic --no-input

VOLUME "$FTLDATA"

# For local or standard use, must match the env var PORT value.
EXPOSE $PORT

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]