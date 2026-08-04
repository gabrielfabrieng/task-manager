#!/bin/sh
# Wait for Postgres, apply migrations, then run the given command.
set -e

echo "Waiting for Postgres at ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
python - <<'PY'
import os, time, socket
host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("Postgres not reachable")
PY

echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files in production (served by WhiteNoise).
if [ "${RUN_COLLECTSTATIC:-0}" = "1" ]; then
  echo "Collecting static files..."
  python manage.py collectstatic --noinput
fi

exec "$@"
