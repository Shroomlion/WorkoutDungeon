from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Character
from .serializers import CharacterSerializer


class MyCharacterView(APIView):
    """GET /api/characters/me/ — the caller's character with derived stats.

    Lazily creates the character on first fetch so there's no separate
    onboarding step to fail.
    """

    def get(self, request):
        character, _ = Character.objects.get_or_create(
            user=request.user, defaults={"name": request.user.username}
        )
        return Response(CharacterSerializer(character).data)
