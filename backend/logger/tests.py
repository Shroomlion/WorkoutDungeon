from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from characters.models import StatEvent
from workouts.models import Exercise, Workout


def formset_management_data(total=6):
    """The hidden bookkeeping fields Django's formset machinery expects
    back on every POST (see log_form.html's management_form)."""
    data = {
        "sets-TOTAL_FORMS": str(total),
        "sets-INITIAL_FORMS": "0",
        "sets-MIN_NUM_FORMS": "0",
        "sets-MAX_NUM_FORMS": "1000",
    }
    for i in range(total):
        for field in ("exercise", "reps", "weight_kg", "duration_seconds", "distance_m"):
            data[f"sets-{i}-{field}"] = ""
    return data


class LoggerViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("hero", password="testpass")
        cls.deadlift = Exercise.objects.create(
            name="Deadlift",
            measurement=Exercise.Measurement.REPS_WEIGHT,
            str_weight=0.8,
            vit_weight=0.2,
        )

    def test_sheet_requires_login(self):
        response = self.client.get(reverse("logger:sheet"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("logger:login"), response.url)

    def test_sheet_renders_derived_scores(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("logger:sheet"))
        self.assertContains(response, "STR")
        self.assertContains(response, "Level 1")

    def test_log_workout_creates_sets_and_stat_events(self):
        self.client.force_login(self.user)
        data = {
            "performed_at": "2026-07-06T10:00",
            "notes": "",
            **formset_management_data(),
        }
        data.update(
            {
                "sets-0-exercise": str(self.deadlift.pk),
                "sets-0-reps": "5",
                "sets-0-weight_kg": "100",
            }
        )
        response = self.client.post(reverse("logger:log"), data)
        self.assertRedirects(response, reverse("logger:sheet"))
        workout = Workout.objects.get(user=self.user)
        self.assertEqual(workout.sets.count(), 1)
        self.assertTrue(StatEvent.objects.filter(workout=workout).exists())

    def test_empty_workout_rejected(self):
        self.client.force_login(self.user)
        data = {
            "performed_at": "2026-07-06T10:00",
            "notes": "",
            **formset_management_data(),
        }
        response = self.client.post(reverse("logger:log"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log at least one movement.")
        self.assertFalse(Workout.objects.exists())

    def test_set_missing_required_field_rejected(self):
        self.client.force_login(self.user)
        data = {
            "performed_at": "2026-07-06T10:00",
            "notes": "",
            **formset_management_data(),
        }
        data.update({"sets-0-exercise": str(self.deadlift.pk), "sets-0-reps": "5"})
        response = self.client.post(reverse("logger:log"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "requires: weight_kg")
        self.assertFalse(Workout.objects.exists())
