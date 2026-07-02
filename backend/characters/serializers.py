from rest_framework import serializers

from . import services
from .models import Character


class CharacterSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = Character
        fields = ["id", "name", "level", "stats", "created_at"]

    def get_stats(self, character):
        return services.ability_scores(character)

    def get_level(self, character):
        return services.character_level(character)
