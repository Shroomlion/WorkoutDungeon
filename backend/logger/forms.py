"""Forms for the server-rendered logger (DECISIONS.md D8).

Same validation rules as the DRF serializers (both import
REQUIRED_SET_FIELDS from workouts.models), different input layer.
"""

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from workouts.models import REQUIRED_SET_FIELDS, SetEntry, Workout


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ["performed_at", "notes"]
        widgets = {
            # format must match the value shape datetime-local inputs expect
            "performed_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class SetEntryForm(forms.ModelForm):
    class Meta:
        model = SetEntry
        fields = ["exercise", "reps", "weight_kg", "duration_seconds", "distance_m"]
        # UI vocabulary: a row is a "movement" (code keeps SetEntry/sets).
        labels = {
            "exercise": "Movement",
            "weight_kg": "Weight (kg)",
            "duration_seconds": "Duration (s)",
            "distance_m": "Distance (m)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exercise"].empty_label = "Choose a movement…"

    def clean(self):
        data = super().clean()
        exercise = data.get("exercise")
        if exercise is None:
            # A fully blank row is fine — the formset skips it entirely.
            return data
        missing = [
            field
            for field in REQUIRED_SET_FIELDS[exercise.measurement]
            if not data.get(field)
        ]
        if missing:
            raise forms.ValidationError(
                f"{exercise.name} ({exercise.get_measurement_display()}) "
                f"requires: {', '.join(missing)}"
            )
        return data


class BaseSetEntryFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        if not any(form.cleaned_data.get("exercise") for form in self.forms):
            raise forms.ValidationError("Log at least one movement.")


# Six fixed blank rows instead of dynamic "add another set" (D8: dynamic
# rows only if real use demands them).
SetEntryFormSet = inlineformset_factory(
    Workout,
    SetEntry,
    form=SetEntryForm,
    formset=BaseSetEntryFormSet,
    extra=6,
    can_delete=False,
)
