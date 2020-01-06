#!/usr/bin/env sh

if [ -z "$CRON_DISABLE" ]; then
  curl http://localhost:$PORT/crons/not-secure/batch-delete-documents
  touch /tmp/batch-delete-docs-last-run
fi

exit 0