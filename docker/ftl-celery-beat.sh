#!/usr/bin/env sh

if [ $CELERY_BEAT_MODE = 'true' ]; then
  cd /app || exit
  celery -A ftl beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
fi
