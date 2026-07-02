# Decisions

Architecture decisions and their rationale, numbered for cross-reference.

## D1 — Public repo, ship-first
The repo is public and every phase ends deployed, so commit and README hygiene
matter from day one. Shipping continuously keeps a live link available at all
times and forces the project through the messy middle where side projects
usually die.

## D2 — Backend is a swappable spine
Django+DRF+Postgres exposes a clean API (log workout -> recompute stats ->
fetch character -> run dungeon). Keeping the contract client-agnostic makes a
future client rebuild (e.g. Godot v2) touch only the client, never the spine.

## D3 — Web-first client, Godot deferred
React proves the core loop with the lowest friction: no install, instant
deploys, one language across the client. Godot stays a v2 option only if game
feel becomes the bottleneck. Phaser itself is deferred until a minimal
React/SVG dungeon proves the loop is fun.

## D4 — Monorepo
Solo dev validating a loop benefits from atomic cross-stack commits and one
place to look. Swappable-client story needs separate directories, not separate
repos.

## D5 — Phased around loop validation; ship every phase
- P0 foundations (repo, data model)
- P1 spine + workout logger -> log a workout, watch character level up (MVP; deploy early so there's always a live link)
- P2 minimal dungeon -> validation gate: does real-workout->in-game-power feel rewarding?
- P3 make it a real game (procedural depth, cosmetic economy, game feel, Phaser likely here)
- P4 tune open questions against real play data

## D6 — Open questions: deferred vs blocking
Only the stack blocked code, and it's resolved. Schema should *allow* stat decay
(timestamped stat events) and a class system (derived attribute, no migration
pain) but ship with both off. Death penalty, floor scaling, access gating,
logging friction, and social layer are tunable/deferrable — they don't block code.

## D7 — Progression model: four fitness-native stats, event-sourced
STR/STA/AGI/VIT — every stat maps to a real workout modality, nothing dormant
(vs. D&D-six where INT/WIS/CHA would idle until Phase 2+). Logging is
set-level (exercise + reps/weight/duration/distance): more friction, but
friction is tunable (D6) and the per-set data is richer forever. Each Exercise
carries per-stat weights (e.g. deadlift 0.8 STR / 0.2 VIT); set volume ×
weights → timestamped StatEvents. Ability scores are *derived* by aggregating
events (sqrt curve), never stored — which is what keeps decay (time-weighted
aggregation) and class systems (derived from stat distribution) open per D6.
All balance tunables live in characters/services.py; formula changes replay
cleanly because workouts are the source of truth.
