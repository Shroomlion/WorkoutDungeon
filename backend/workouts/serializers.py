from rest_framework import serializers

from .models import Exercise, SetEntry, Workout


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            "id",
            "name",
            "measurement",
            "str_weight",
            "sta_weight",
            "agi_weight",
            "vit_weight",
        ]


# Which SetEntry fields each measurement type requires.
_REQUIRED_FIELDS = {
    Exercise.Measurement.REPS_WEIGHT: ["reps", "weight_kg"],
    Exercise.Measurement.REPS: ["reps"],
    Exercise.Measurement.DURATION: ["duration_seconds"],
    Exercise.Measurement.DISTANCE: ["distance_m"],
}


class SetEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SetEntry
        fields = [
            "id",
            "exercise",
            "order",
            "reps",
            "weight_kg",
            "duration_seconds",
            "distance_m",
        ]

    def validate(self, data):
        exercise = data["exercise"]
        missing = [
            field
            for field in _REQUIRED_FIELDS[exercise.measurement]
            if data.get(field) in (None, 0)
        ]
        if missing:
            raise serializers.ValidationError(
                f"{exercise.name} ({exercise.get_measurement_display()}) "
                f"requires: {', '.join(missing)}"
            )
        return data


class WorkoutSerializer(serializers.ModelSerializer):
    sets = SetEntrySerializer(many=True)
    stat_gains = serializers.SerializerMethodField()

    class Meta:
        model = Workout
        fields = ["id", "performed_at", "notes", "sets", "stat_gains", "created_at"]
        read_only_fields = ["created_at"]

    def get_stat_gains(self, workout):
        """XP this workout granted, so the client can show the payoff
        immediately — the core loop's reward beat."""
        return {event.stat: round(event.amount, 2) for event in workout.stat_events.all()}

    def create(self, validated_data):
        sets_data = validated_data.pop("sets")
        workout = Workout.objects.create(**validated_data)
        SetEntry.objects.bulk_create(
            SetEntry(workout=workout, **set_data) for set_data in sets_data
        )
        return workout

    def update(self, instance, validated_data):
        sets_data = validated_data.pop("sets", None)
        instance = super().update(instance, validated_data)
        if sets_data is not None:
            instance.sets.all().delete()
            SetEntry.objects.bulk_create(
                SetEntry(workout=instance, **set_data) for set_data in sets_data
            )
        return instance
