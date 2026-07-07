# Workout Dungeon

Real workouts power a character in a roguelite dungeon crawler. Log your
actual training — sets, reps, weight, distance — and your character's
ability scores grow from it.

**The core loop:** log a workout → the progression engine converts effort
into stat XP → your character levels up → (Phase 2) take that character
into the dungeon.

## How progression works

Every exercise in the catalog carries per-stat weights across four
fitness-native abilities — **STR / STA / AGI / VIT** — so every stat maps
to a real training modality (a deadlift is 0.8 STR / 0.2 VIT; a run is
0.8 STA / 0.2 AGI). Set volume × weights produces timestamped
**StatEvents**, and ability scores are *derived* by aggregating those
events through a sqrt curve — never stored.

Because progression is event-sourced, rebalancing a formula is just
"delete events, replay workouts", and planned mechanics like stat decay
(time-weighted aggregation) or a class system (derived from your stat
distribution) need no schema changes. All balance tunables live in one
place: [`backend/characters/services.py`](backend/characters/services.py).

## Architecture

- **Django + DRF + PostgreSQL** backend — the "spine". The REST API is
  deliberately client-agnostic: routes describe the domain (workouts,
  exercises, characters), never a specific frontend, so future clients
  swap in without touching the backend.
- **Hybrid client strategy.** The workout logger is server-rendered
  Django templates (forms-and-tables ship fastest that way, one
  deployable app); the dungeon will be a React SPA (already scaffolded in
  [`frontend/`](frontend/)) because it's irreducibly client-side.
  Template views and the API call the same service layer.
- **Monorepo** — solo project validating a game loop benefits from atomic
  cross-stack commits.

Architecture decisions and their rationale are logged in
[DECISIONS.md](DECISIONS.md).

## Roadmap

| Phase | Scope | Status |
|-------|-------|--------|
| P0 | Foundations: repo, data model | ✅ |
| P1 | Spine + workout logger — log a workout, watch your character level up | 🔨 in progress |
| P2 | Minimal dungeon — the validation gate: does real-workout → in-game-power feel rewarding? | |
| P3 | Make it a real game: procedural depth, game feel | |
| P4 | Tune balance against real play data | |

Every phase ends deployed.

## Running locally

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/), and PostgreSQL.

```bash
# Backend
cd backend
cp .env.example .env          # then set SECRET_KEY and DB_* values
createdb workout_dungeon
uv sync
uv run manage.py migrate
uv run manage.py loaddata exercises   # seed the exercise catalog
uv run manage.py createsuperuser

# From the repo root — start/stop the dev server, run the test suite
./scripts/start.sh            # logger UI at http://localhost:8000/
./scripts/stop.sh
./scripts/test.sh
```

The API lives under `/api/` (session-authenticated); the server-rendered
logger is at the site root. The React scaffold in `frontend/` (`npm
install && npm run dev`) proxies `/api` to Django but is parked until
Phase 2.

## License

Source-available for viewing and educational purposes — see
[LICENSE](LICENSE).
