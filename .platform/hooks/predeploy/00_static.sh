#!/usr/bin/env bash
mkdir -p /var/app/current/static
source /var/app/venv/staging-LQM1lest/bin/activate && python manage.py static
chown -R webapp:webapp /var/app/current/static
