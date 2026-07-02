from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Exercise(models.Model):
    """Catalog entry: what an exercise is and which stats it trains.

    Stat weights are the tunable mapping from real effort to character
    progression (DECISIONS.md D5/P4): each weight is the fraction of this
    exercise's volume credited to that stat. They don't have to sum to 1 —
    an exercise that trains everything hard can sum higher.
    """

    class Measurement(models.TextChoices):
        REPS_WEIGHT = "reps_weight", "Reps × weight"
        REPS = "reps", "Reps only (bodyweight)"
        DURATION = "duration", "Duration"
        DISTANCE = "distance", "Distance"

    name = models.CharField(max_length=100, unique=True)
    measurement = models.CharField(max_length=20, choices=Measurement.choices)

    str_weight = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    sta_weight = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    agi_weight = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    vit_weight = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Workout(models.Model):
    """A logged workout session; the unit the whole loop hangs off of:
    log workout -> recompute stats -> fetch character (D2)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workouts",
    )
    performed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-performed_at"]

    def __str__(self):
        return f"{self.user} @ {self.performed_at:%Y-%m-%d %H:%M}"


class SetEntry(models.Model):
    """One set within a workout.

    Which fields are required depends on the exercise's measurement type
    (enforced in the serializer, not the DB, so the catalog stays flexible):
      reps_weight -> reps + weight_kg
      reps        -> reps
      duration    -> duration_seconds
      distance    -> distance_m
    Stored in metric; clients convert for display.
    """

    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name="sets",
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name="set_entries",
    )
    order = models.PositiveIntegerField(default=0)
    reps = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    distance_m = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "set entries"

    def __str__(self):
        return f"{self.exercise} (workout {self.workout_id})"
