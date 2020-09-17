#!/usr/bin/env sh

if [ -z "$CRON_DISABLE" ]; then
  curl -H "X-Appengine-Cron: true" http://localhost:$PORT/crons_core/$CRON_SECRET_KEY/batch_delete_documents
  touch /tmp/batch-delete-docs-last-run
fi
