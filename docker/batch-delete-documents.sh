#!/usr/bin/env sh

if [ -z "$CRON_DISABLE" ]; then
  curl -H "X-Appengine-Cron: true" http://localhost:$PORT/crons/$CRON_SECRET_KEY/batch-delete-documents
  touch /tmp/batch-delete-docs-last-run
fi
