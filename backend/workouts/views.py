from rest_framework import viewsets

from characters import services

from .models import Exercise
from .serializers import ExerciseSerializer, WorkoutSerializer


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """The exercise catalog. Read-only over the API; managed via admin."""

    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer


class WorkoutViewSet(viewsets.ModelViewSet):
    """Log and browse your own workouts.

    Creating or editing a workout immediately (re)applies its stat events —
    the D2 loop: log workout -> recompute stats -> fetch character.
    """

    serializer_class = WorkoutSerializer

    def get_queryset(self):
        return self.request.user.workouts.prefetch_related("sets", "stat_events")

    def perform_create(self, serializer):
        workout = serializer.save(user=self.request.user)
        services.apply_workout(workout)

    def perform_update(self, serializer):
        workout = serializer.save()
        services.apply_workout(workout)
