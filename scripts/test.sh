#!/usr/bin/env bash
# Run the backend test suite. Extra args pass through to manage.py test,
# e.g.:  ./scripts/test.sh characters            (one app)
#        ./scripts/test.sh workouts.tests.WorkoutAPITests.test_requires_auth
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/backend"

exec .venv/bin/python manage.py test "$@"
