#!/usr/bin/env sh

env | grep 'CRON_DISABLE' >> /etc/environment
env | grep 'PORT' >> /etc/environment
env | grep 'CRON_SECRET_KEY' >> /etc/environment
