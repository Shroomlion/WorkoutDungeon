"""Server-rendered logger views (DECISIONS.md D8).

These call the service layer directly — same domain spine as the DRF API,
no JSON round-trip. The API remains the contract for the P2 game client.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from characters.models import Character
from characters.services import (
    ability_scores,
    apply_workout,
    level_from_xp,
    xp_needed_for_level,
)
from workouts.models import REQUIRED_SET_FIELDS, Exercise

from .forms import SetEntryFormSet, WorkoutForm


@login_required
def sheet(request):
    # Lazily create the character, same as the API's /characters/me/.
    character, _ = Character.objects.get_or_create(
        user=request.user, defaults={"name": request.user.username}
    )
    # One aggregation query; level and both "XP to next" numbers are derived
    # from it in Python rather than re-querying per stat.
    scores = ability_scores(character)
    total_xp = sum(stat["xp"] for stat in scores.values())
    level = level_from_xp(total_xp)
    return render(
        request,
        "logger/sheet.html",
        {
            "character": character,
            "level": level,
            "scores": scores,
            "xp_to_next_level": round(xp_needed_for_level(level + 1) - total_xp, 1),
        },
    )


@login_required
def log_workout(request):
    # exercise id -> fields its measurement type needs; derived from the
    # same REQUIRED_SET_FIELDS the validators use, and shipped to the
    # page's JS so it can hide the irrelevant inputs (UX only — the form
    # validation stays the enforcement).
    field_map = {
        exercise.pk: REQUIRED_SET_FIELDS[exercise.measurement]
        for exercise in Exercise.objects.all()
    }
    if request.method == "POST":
        form = WorkoutForm(request.POST)
        formset = SetEntryFormSet(request.POST, prefix="sets")
        if form.is_valid() and formset.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            formset.instance = workout
            for order, entry in enumerate(formset.save(commit=False)):
                entry.order = order
                entry.save()
            events = apply_workout(workout)
            gains = ", ".join(f"+{event.amount:.1f} {event.stat}" for event in events)
            messages.success(request, f"Workout logged! {gains}")
            return redirect("logger:sheet")
    else:
        form = WorkoutForm()
        formset = SetEntryFormSet(prefix="sets")
    return render(
        request,
        "logger/log_form.html",
        {"form": form, "formset": formset, "field_map": field_map},
    )
