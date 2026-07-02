"""Progression engine: turns logged workouts into stat XP and ability scores.

All game-balance tunables live at the top of this module (DECISIONS.md D5/P4:
tune against real play data). Because StatEvents are event-sourced, changing
a formula only requires deleting events and replaying workouts through
apply_workout() — no schema changes.
"""

import math

from django.db import transaction
from django.db.models import Sum

from workouts.models import Exercise, SetEntry, Workout

from .models import Character, Stat, StatEvent

# --- Tunables ---------------------------------------------------------------

# Base XP per unit of effort, normalized so a typical solid session of any
# modality lands in the same ballpark (~50-150 XP).
XP_PER_KG_REP = 0.01  # reps_weight: 3x8 @ 100kg -> 24 XP
XP_PER_BODYWEIGHT_REP = 0.5  # reps: 3x15 pushups -> 22.5 XP
XP_PER_MINUTE = 1.0  # duration: 30 min -> 30 XP
XP_PER_KM = 5.0  # distance: 5 km -> 25 XP

BASE_SCORE = 8  # every stat starts here, D&D-commoner style
SCORE_XP_SCALE = 25.0  # +1 score at 25 XP, +2 at 100, +3 at 225 (sqrt curve)

LEVEL_XP_SCALE = 100.0  # level 2 at 100 total XP, 3 at 400, 4 at 900

_STAT_WEIGHT_FIELDS = {
    Stat.STRENGTH: "str_weight",
    Stat.STAMINA: "sta_weight",
    Stat.AGILITY: "agi_weight",
    Stat.VITALITY: "vit_weight",
}

# --- XP math ----------------------------------------------------------------


def set_base_xp(entry: SetEntry) -> float:
    """Raw effort XP for one set, before stat weights are applied."""
    match entry.exercise.measurement:
        case Exercise.Measurement.REPS_WEIGHT:
            return (entry.reps or 0) * (entry.weight_kg or 0) * XP_PER_KG_REP
        case Exercise.Measurement.REPS:
            return (entry.reps or 0) * XP_PER_BODYWEIGHT_REP
        case Exercise.Measurement.DURATION:
            return (entry.duration_seconds or 0) / 60 * XP_PER_MINUTE
        case Exercise.Measurement.DISTANCE:
            return (entry.distance_m or 0) / 1000 * XP_PER_KM
    return 0.0


def score_from_xp(xp: float) -> int:
    """Ability score for a stat's accumulated XP. Sqrt curve: each point
    costs progressively more, so early gains feel fast."""
    return BASE_SCORE + math.floor(math.sqrt(max(xp, 0) / SCORE_XP_SCALE))


def level_from_xp(total_xp: float) -> int:
    return 1 + math.floor(math.sqrt(max(total_xp, 0) / LEVEL_XP_SCALE))


# --- The loop ---------------------------------------------------------------


@transaction.atomic
def apply_workout(workout: Workout) -> list[StatEvent]:
    """Convert a workout's sets into StatEvents for the user's character.

    Idempotent: re-applying (e.g. after the workout is edited) replaces the
    workout's previous events rather than stacking them.
    """
    character, _ = Character.objects.get_or_create(
        user=workout.user, defaults={"name": workout.user.username}
    )
    workout.stat_events.all().delete()

    gains: dict[str, float] = {}
    for entry in workout.sets.select_related("exercise"):
        base_xp = set_base_xp(entry)
        for stat, field in _STAT_WEIGHT_FIELDS.items():
            weight = getattr(entry.exercise, field)
            if weight > 0:
                gains[stat] = gains.get(stat, 0.0) + base_xp * weight

    events = [
        StatEvent(character=character, stat=stat, amount=amount, workout=workout)
        for stat, amount in gains.items()
        if amount > 0
    ]
    return StatEvent.objects.bulk_create(events)


def ability_scores(character: Character) -> dict[str, dict]:
    """Current derived scores for every stat.

    Plain sum for now; when decay ships (D6), this becomes a time-weighted
    aggregation over the same events.
    """
    totals = dict(
        character.stat_events.values_list("stat")
        .annotate(total=Sum("amount"))
        .values_list("stat", "total")
    )
    return {
        stat.value: {
            "score": score_from_xp(totals.get(stat.value, 0.0)),
            "xp": round(totals.get(stat.value, 0.0), 2),
        }
        for stat in Stat
    }


def character_level(character: Character) -> int:
    total = character.stat_events.aggregate(total=Sum("amount"))["total"] or 0.0
    return level_from_xp(total)
