from django.contrib import admin

from .models import Character, StatEvent


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "created_at"]


@admin.register(StatEvent)
class StatEventAdmin(admin.ModelAdmin):
    """Read-only: events are produced by the progression engine, not by hand."""

    list_display = ["character", "stat", "amount", "workout", "created_at"]
    list_filter = ["stat"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
