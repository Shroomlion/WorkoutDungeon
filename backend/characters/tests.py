from django.contrib.auth import get_user_model
from django.test import TestCase

from workouts.models import Exercise, SetEntry, Workout

from . import services
from .models import Character, Stat, StatEvent

User = get_user_model()


class ScoreMathTests(TestCase):
    def test_score_starts_at_base(self):
        self.assertEqual(services.score_from_xp(0), services.BASE_SCORE)

    def test_score_follows_sqrt_curve(self):
        scale = services.SCORE_XP_SCALE
        self.assertEqual(services.score_from_xp(scale), services.BASE_SCORE + 1)
        self.assertEqual(services.score_from_xp(4 * scale), services.BASE_SCORE + 2)
        self.assertEqual(services.score_from_xp(9 * scale), services.BASE_SCORE + 3)

    def test_level_starts_at_one(self):
        self.assertEqual(services.level_from_xp(0), 1)


class ApplyWorkoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="hero", password="x")
        cls.deadlift = Exercise.objects.create(
            name="Deadlift",
            measurement=Exercise.Measurement.REPS_WEIGHT,
            str_weight=0.8,
            vit_weight=0.2,
        )
        cls.running = Exercise.objects.create(
            name="Run",
            measurement=Exercise.Measurement.DISTANCE,
            sta_weight=0.8,
            agi_weight=0.2,
        )

    def _workout_with_deadlifts(self):
        workout = Workout.objects.create(user=self.user)
        # 3x5 @ 100kg -> 1500 kg-reps -> 15 base XP
        for i in range(3):
            SetEntry.objects.create(
                workout=workout, exercise=self.deadlift, order=i, reps=5, weight_kg=100
            )
        return workout

    def test_creates_character_and_weighted_events(self):
        workout = self._workout_with_deadlifts()
        services.apply_workout(workout)

        character = Character.objects.get(user=self.user)
        events = {e.stat: e.amount for e in character.stat_events.all()}
        base_xp = 1500 * services.XP_PER_KG_REP
        self.assertAlmostEqual(events[Stat.STRENGTH], base_xp * 0.8)
        self.assertAlmostEqual(events[Stat.VITALITY], base_xp * 0.2)
        self.assertNotIn(Stat.STAMINA, events)

    def test_reapply_is_idempotent(self):
        workout = self._workout_with_deadlifts()
        services.apply_workout(workout)
        services.apply_workout(workout)

        self.assertEqual(StatEvent.objects.filter(workout=workout).count(), 2)

    def test_ability_scores_aggregate_all_events(self):
        workout = self._workout_with_deadlifts()
        services.apply_workout(workout)
        character = Character.objects.get(user=self.user)

        scores = services.ability_scores(character)
        self.assertEqual(set(scores), {"STR", "STA", "AGI", "VIT"})
        # 12 STR XP -> still base score; untrained stats sit at base too
        self.assertEqual(scores["STR"]["score"], services.BASE_SCORE)
        self.assertAlmostEqual(scores["STR"]["xp"], 12.0)
        self.assertEqual(scores["STA"]["score"], services.BASE_SCORE)
        # Next score point sits at SCORE_XP_SCALE (the score curve, not the
        # level curve): 25 XP threshold - 12 earned = 13 to go.
        self.assertAlmostEqual(
            scores["STR"]["xp_to_next"], services.SCORE_XP_SCALE - 12.0
        )
        self.assertAlmostEqual(scores["STA"]["xp_to_next"], services.SCORE_XP_SCALE)
        # 12 of the 25 XP in the first bracket -> 48% through it
        self.assertEqual(scores["STR"]["progress"], 48)
        self.assertEqual(scores["STA"]["progress"], 0)

    def test_distance_exercise_grants_stamina(self):
        workout = Workout.objects.create(user=self.user)
        SetEntry.objects.create(
            workout=workout, exercise=self.running, distance_m=5000
        )  # 5 km -> 25 base XP
        services.apply_workout(workout)

        character = Character.objects.get(user=self.user)
        events = {e.stat: e.amount for e in character.stat_events.all()}
        base_xp = 5 * services.XP_PER_KM
        self.assertAlmostEqual(events[Stat.STAMINA], base_xp * 0.8)
        self.assertAlmostEqual(events[Stat.AGILITY], base_xp * 0.2)
