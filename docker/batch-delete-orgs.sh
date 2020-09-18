#!/usr/bin/env sh

if [ -z "$CRON_DISABLE" ]; then
  curl -H "X-Appengine-Cron: true" http://localhost:$PORT/crons_account/$CRON_SECRET_KEY/batch_delete_orgs
  touch /tmp/batch-delete-orgs-last-run
fi
