from django.conf import settings
from django.db import models


class Stat(models.TextChoices):
    """The four fitness-native ability scores.

    Kept as a TextChoices enum so adding a stat later is a one-line change
    plus a migration on StatEvent's choices (cheap — choices aren't enforced
    at the DB level in Django).
    """

    STRENGTH = "STR", "Strength"
    STAMINA = "STA", "Stamina"
    AGILITY = "AGI", "Agility"
    VITALITY = "VIT", "Vitality"


class Character(models.Model):
    """One character per user.

    Deliberately thin: ability scores and level are *derived* from StatEvent
    rows (see services.py), never stored here. That's what keeps stat decay
    and a class system possible without migrations (DECISIONS.md D6).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="character",
    )
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StatEvent(models.Model):
    """A timestamped grant of stat XP, usually sourced from a workout.

    This is the event-sourced core of progression (D6): ability scores are
    computed by aggregating events, so decay (time-weighted aggregation) or
    formula changes (delete + replay from workouts) never require schema
    changes.
    """

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="stat_events",
    )
    stat = models.CharField(max_length=3, choices=Stat.choices)
    amount = models.FloatField(help_text="Stat XP granted (not score points).")
    workout = models.ForeignKey(
        "workouts.Workout",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="stat_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["character", "stat"])]

    def __str__(self):
        return f"{self.character} +{self.amount:.1f} {self.stat}"
