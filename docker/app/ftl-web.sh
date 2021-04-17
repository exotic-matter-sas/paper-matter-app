#!/usr/bin/env sh

if [ $WEB_MODE = 'true' ]; then
  uwsgi --ini /app/ftl_uwsgi.ini
fi
