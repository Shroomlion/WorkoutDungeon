from django.contrib import admin

from .models import Exercise, SetEntry, Workout


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "measurement",
        "str_weight",
        "sta_weight",
        "agi_weight",
        "vit_weight",
    ]
    list_filter = ["measurement"]
    search_fields = ["name"]


class SetEntryInline(admin.TabularInline):
    model = SetEntry
    extra = 0


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ["user", "performed_at", "created_at"]
    list_filter = ["performed_at"]
    inlines = [SetEntryInline]
