"""URL configuration — the API contract lives here (DECISIONS.md D2).

Keep it client-agnostic: routes describe the domain (workouts, exercises,
characters), never a specific frontend.
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from characters.views import MyCharacterView
from workouts.views import ExerciseViewSet, WorkoutViewSet

router = DefaultRouter()
router.register("exercises", ExerciseViewSet, basename="exercise")
router.register("workouts", WorkoutViewSet, basename="workout")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/characters/me/", MyCharacterView.as_view(), name="my-character"),
]
