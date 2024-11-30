#!/bin/bash

# Iniciar o worker Celery em background
celery -A tasks worker --loglevel=info &

# Iniciar a API
uvicorn api:app --host 0.0.0.0 --port 8080