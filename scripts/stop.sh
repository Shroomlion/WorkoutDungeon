#!/usr/bin/env bash
# Stop the Django dev server started by start.sh.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIDFILE="$ROOT/.server.pid"

if [[ -f "$PIDFILE" ]]; then
    PID="$(cat "$PIDFILE")"
    if kill -0 "$PID" 2>/dev/null; then
        # Negative PID = kill the whole process group (server + autoreloader).
        kill -- "-$PID" 2>/dev/null || kill "$PID"
        echo "Server stopped (PID $PID)."
    else
        echo "Stale PID file (process $PID not running); cleaning up."
    fi
    rm -f "$PIDFILE"
else
    # Fallback: catch a server started by hand.
    if pkill -f "manage.py runserver"; then
        echo "Server stopped (found via pkill; no PID file)."
    else
        echo "No server running."
    fi
fi
