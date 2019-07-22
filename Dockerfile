FROM node:10.15.3-alpine AS frontdependencies
ADD /ftl/frontend/package*.json /app/
WORKDIR /app
RUN npm ci



FROM frontdependencies AS frontbuild
COPY /ftl/frontend /app
WORKDIR /app
RUN npm run build



FROM python:3.7.3-stretch AS backendbuild
RUN apt-get update && apt-get install -y --no-install-recommends gettext
COPY /ftl /app
ADD docker/requirements.txt /app/requirements.txt
ADD docker/settings.py /app/ftl/settings.py
WORKDIR /app
RUN python3 -m pip install -r requirements.txt
RUN python3 manage.py compilemessages



FROM python:3.7.3-alpine3.10
ENV PORT 8000
ADD docker/requirements.txt /app/requirements.txt

RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev python3-dev build-base linux-headers pcre-dev && \
 python3 -m pip install -r /app/requirements.txt --no-cache-dir && \
 python3 -m pip install uwsgi && \
 apk --purge del .build-deps

RUN apk add --no-cache postgresql-libs openjdk11-jre pcre && rm -rf /var/cache/apk/*

ADD docker/ftl_uwsgi.ini /app/ftl_uwsgi.ini
ADD docker/settings.py /app/ftl/settings.py

# Those RUN true commands are a workaround for https://github.com/moby/moby/issues/37965
ADD ftl /app/
COPY --from=backendbuild /app/core/locale /app/core/locale
RUN true
COPY --from=backendbuild /app/frontend/locale /app/frontend/locale
RUN true
COPY --from=backendbuild /app/setup/locale /app/setup/locale
RUN true
COPY --from=frontbuild /app/dist /app/frontend/dist
RUN true
COPY --from=frontbuild /app/pdfjs /app/frontend/pdfjs
RUN true
COPY --from=frontbuild /app/webpack-stats.json /app/frontend/
RUN true
COPY --from=frontbuild /app/__init__.py /app/frontend/

WORKDIR /app

RUN python3 -m compileall ./
RUN python3 manage.py collectstatic --no-input

VOLUME /app/uploads

# For local or standard use, the expose command is not used by Heroku
EXPOSE 8000

# Run the image as a non-root user
RUN adduser -D ftl
USER ftl

CMD uwsgi --ini /app/ftl_uwsgi.ini
