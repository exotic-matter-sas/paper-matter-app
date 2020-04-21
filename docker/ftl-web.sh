#!/usr/bin/env sh

if [ $WEB_MODE = 'true' ]; then
  /usr/local/bin/uwsgi --ini /app/ftl_uwsgi.ini
fi
