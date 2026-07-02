#!/usr/bin/env bash
# Start the Django dev server in the background.
# Usage: ./scripts/start.sh [port]   (default: 8000)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
PIDFILE="$ROOT/.server.pid"
LOGFILE="$ROOT/server.log"
PORT="${1:-8000}"

# Already running?
if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "Server already running (PID $(cat "$PIDFILE")) -> http://localhost:$PORT"
    exit 0
fi

# Preflight: Postgres must be up before Django can do anything useful.
if ! pg_isready -h localhost -p 5432 -q; then
    echo "ERROR: Postgres is not accepting connections on localhost:5432" >&2
    echo "       (WSL tip: 'sudo service postgresql start')" >&2
    exit 1
fi

cd "$BACKEND"

# Apply any pending migrations so the server never runs against a stale schema.
.venv/bin/python manage.py migrate --no-input

# setsid puts the server in its own process group, so stop.sh can kill the
# whole group (runserver's autoreloader spawns a child process).
setsid .venv/bin/python manage.py runserver "0.0.0.0:$PORT" >"$LOGFILE" 2>&1 &
echo $! > "$PIDFILE"

# Wait for it to answer before declaring victory.
for _ in $(seq 1 20); do
    if curl -s -o /dev/null "http://localhost:$PORT/api/"; then
        echo "Server running (PID $(cat "$PIDFILE"))"
        echo "  API:   http://localhost:$PORT/api/"
        echo "  Admin: http://localhost:$PORT/admin/"
        echo "  Logs:  tail -f $LOGFILE"
        exit 0
    fi
    sleep 0.5
done

echo "ERROR: server did not come up — check $LOGFILE" >&2
exit 1
