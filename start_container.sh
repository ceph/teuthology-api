#!/usr/bin/bash
set -ex
trap exit TERM

HOST=${TEUTHOLOGY_API_SERVER_HOST:-"0.0.0.0"}
PORT=${TEUTHOLOGY_API_SERVER_PORT:-"8082"}
VENV=${VENV:-"venv"}

source ${VENV}/bin/activate
alembic -x verbose=1 upgrade head

cd /teuthology_api/src/

if [ "$DEPLOYMENT" = "development" ]; then
  uvicorn teuthology_api.main:app --reload --port $PORT --host $HOST
else
  gunicorn -c /teuthology_api/gunicorn_config.py teuthology_api.main:app
fi
