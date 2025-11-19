#!/usr/bin/env sh
set -eu

PG_USERNAME=${PG_USERNAME:-"postgres"}
PG_PASSWORD=${PG_PASSWORD:-"password"}
PG_HOST=${PG_HOST:-"postgres"}
PG_PORT=${PG_PORT:-5432}
PG_NAME=${PG_NAME:-"postgres"}
DATABASE_URL="postgresql+asyncpg://${PG_USERNAME}:${PG_PASSWORD}@${PG_HOST}:${PG_PORT}/${PG_NAME}"
echo "Using DATABASE_URL=${DATABASE_URL}"

MAX_RETRIES=${DB_WAIT_RETRIES:-30}
SLEEP_SEC=${DB_WAIT_SLEEP:-2}
count=0

echo "Waiting for DB on: $PG_HOST:$PG_PORT"
while ! (python - <<PY
import socket, sys
s = socket.socket()
s.settimeout(1.5)
try:
    print("Python trying to connect $PG_HOST:$PG_PORT")
    s.connect(("$PG_HOST", int($PG_PORT)))
    s.close()
    sys.exit(0)
except Exception as e:
    print(e)
    sys.exit(1)
PY
); do
  count=$((count+1))
  if [ "$count" -ge "$MAX_RETRIES" ]; then
    echo
    echo "ERROR: could not connect to ${PG_HOST}:${PG_PORT} after ${MAX_RETRIES} attempts."
    exit 1
  fi
  printf "."
  sleep "$SLEEP_SEC"
done
echo "OK"

echo "Running alembic upgrade head..."
alembic upgrade head

echo "Starting server..."
gunicorn src.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${APP_PORT:-8000} "$@"
