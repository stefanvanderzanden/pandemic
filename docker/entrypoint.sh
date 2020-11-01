#!/bin/sh

python manage.py migrate
python manage.py loaddata game-setup.json
python manage.py runserver 0.0.0.0:8000

exec "$@"
