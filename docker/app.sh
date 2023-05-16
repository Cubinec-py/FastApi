#!/bin/bash

alembic upgrade head

cd src

#gunicorn main:app --reload --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=app:8000 --max-requests 1000
gunicorn --capture-output main:app -c settings/gunicorn.py