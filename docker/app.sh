#!/bin/bash

alembic upgrade head

gunicorn --capture-output src.main:app --chdir /fastapi_app -c src/settings/gunicorn.py