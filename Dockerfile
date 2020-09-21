FROM node:lts-alpine AS frontdependencies
ADD /ftl/frontend/package*.json /app/
WORKDIR /app
RUN npm ci



FROM frontdependencies AS frontbuild
COPY /ftl/frontend /app
WORKDIR /app
RUN npm run build



FROM python:3.7-slim

# Configure the listening PORT for the web frontend server (used by uwsgi)
ENV PORT 8000
# Set to "true" to use this image as a web frontend
ENV ENABLE_WEB false
# Set to "true" to use this image as a worker
ENV ENABLE_WORKER false
# Set number of workers for async processing such as OCR
ENV NB_WORKERS 1
# Set time limit in seconds for each job in async processing (child process will be force restart)
ENV JOB_TIMELIMIT 900

# WARNING: NOT SECURE FOR PRODUCTION
# ===================================
# For production use, additional ENV variables have to be defined to update default security settings.
# The recommanded way to set theses variables is to set them at runtime (either via docker command or via your
# deployment method). Refer to SELFHOSTING.MD for the list of ENV available.

# Run the image as a non-root user
RUN groupadd --gid 1000 ftl \
    && useradd --uid 1000 --gid ftl --shell /bin/bash --create-home ftl

# Workaround for https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=863199
RUN mkdir -p /usr/share/man/man1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext \
    openjdk-11-jre-headless \
    build-essential \
    python3-dev \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    cron \
    supervisor \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

ADD ftl/requirements.txt /app/requirements.txt
ADD docker/requirements_deploy.txt /app/requirements_deploy.txt
ADD docker/ftl_uwsgi.ini /app/ftl_uwsgi.ini
ADD docker/settings_local.py /app/ftl/settings_local.py
ADD --chown=root:root docker/supervisord.conf /etc/supervisor/supervisord.conf

ADD --chown=ftl:ftl docker/ftl-web.sh /app/ftl-web.sh
RUN chmod 0700 /app/ftl-web.sh

ADD --chown=ftl:ftl docker/ftl-worker.sh /app/ftl-worker.sh
RUN chmod 0700 /app/ftl-worker.sh

ADD docker/cron-env-init.sh /tmp/cron-env-init.sh
RUN chmod 0700 /tmp/cron-env-init.sh
RUN chown root:root /tmp/cron-env-init.sh

ADD docker/crontab /etc/cron.d/ftl
RUN chmod 0700 /etc/cron.d/ftl

ADD --chown=root:root docker/batch-delete-documents.sh /etc/cron.hourly/batch-delete-documents
RUN chmod 0700 /etc/cron.hourly/batch-delete-documents

ADD --chown=root:root docker/batch-delete-orgs.sh /etc/cron.daily/batch-delete-orgs
RUN chmod 0700 /etc/cron.daily/batch-delete-orgs

RUN python3 -m pip install -r /app/requirements.txt --no-cache-dir && \
 python3 -m pip install -r /app/requirements_deploy.txt --no-cache-dir

RUN apt-get remove --purge -y build-essential
RUN apt-get autoremove -y


ADD --chown=ftl:ftl ftl /app/

COPY --chown=ftl:ftl --from=frontbuild /app/dist /app/frontend/dist
COPY --chown=ftl:ftl --from=frontbuild /app/pdfjs /app/frontend/pdfjs
COPY --chown=ftl:ftl --from=frontbuild /app/webpack-stats.json /app/frontend/
COPY --chown=ftl:ftl --from=frontbuild /app/__init__.py /app/frontend/

WORKDIR /app

RUN python3 -m compileall ./
RUN python3 manage.py compilemessages
RUN python3 manage.py collectstatic --no-input

RUN chown -R ftl:ftl /app

ENV FTLDATA /app/uploads
RUN mkdir -p "$FTLDATA" && chown -R ftl:ftl "$FTLDATA" && chmod 777 "$FTLDATA"
VOLUME /app/uploads

# For local or standard use, must match the env var PORT value.
EXPOSE $PORT

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]