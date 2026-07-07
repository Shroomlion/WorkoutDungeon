from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from characters.models import StatEvent

from .models import Exercise, Workout

User = get_user_model()


class WorkoutAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="hero", password="x")
        cls.bench = Exercise.objects.create(
            name="Bench Press",
            measurement=Exercise.Measurement.REPS_WEIGHT,
            str_weight=0.9,
            vit_weight=0.1,
        )

    def setUp(self):
        self.client.force_authenticate(self.user)

    def _log_bench_workout(self):
        return self.client.post(
            "/api/workouts/",
            {
                "notes": "push day",
                "sets": [
                    {"exercise": self.bench.pk, "order": 0, "reps": 8, "weight_kg": 60},
                    {"exercise": self.bench.pk, "order": 1, "reps": 8, "weight_kg": 60},
                ],
            },
            format="json",
        )

    def test_requires_auth(self):
        self.client.force_authenticate(None)
        response = self.client.get("/api/workouts/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_log_workout_creates_sets_and_stat_gains(self):
        response = self._log_bench_workout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        workout = Workout.objects.get(pk=response.data["id"])
        self.assertEqual(workout.sets.count(), 2)
        self.assertEqual(StatEvent.objects.filter(workout=workout).count(), 2)
        self.assertIn("STR", response.data["stat_gains"])

    def test_set_fields_validated_against_measurement(self):
        response = self.client.post(
            "/api/workouts/",
            {"sets": [{"exercise": self.bench.pk, "reps": 8}]},  # missing weight_kg
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_workouts_are_scoped_to_owner(self):
        self._log_bench_workout()
        other = User.objects.create_user(username="rival", password="x")
        self.client.force_authenticate(other)

        response = self.client.get("/api/workouts/")
        self.assertEqual(response.data["count"] if "count" in response.data else len(response.data), 0)

    def test_character_endpoint_reflects_workout(self):
        self._log_bench_workout()
        response = self.client.get("/api/characters/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["level"], 1)
        # 2x8x60 = 960 kg-reps -> 9.6 XP -> 8.64 STR XP
        self.assertAlmostEqual(response.data["stats"]["STR"]["xp"], 8.64)
