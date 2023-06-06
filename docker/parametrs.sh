#!/bin/bash

celery -A src.tasks.tasks worker --autoscale=5,2 -l INFO