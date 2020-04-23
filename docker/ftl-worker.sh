#!/usr/bin/env sh

if [ $WORKER_MODE = 'true' ]; then
  cd /app || exit
  celery -A ftl worker -l info --concurrency=$NB_WORKERS
fi
