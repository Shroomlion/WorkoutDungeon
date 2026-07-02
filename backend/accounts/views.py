"""Session-auth endpoints for the SPA.

The flow the React client follows:
  1. GET  /api/auth/csrf/   -> sets the csrftoken cookie
  2. POST /api/auth/login/  -> sets the sessionid cookie
  3. GET  /api/auth/csrf/   again (login rotates the CSRF token)
  4. ...authenticated requests with X-CSRFToken header...
  5. POST /api/auth/logout/
"""

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


@ensure_csrf_cookie
def csrf(request):
    """Plain Django view whose only job is to hand out the CSRF cookie."""
    return JsonResponse({"detail": "CSRF cookie set"})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = authenticate(
            request,
            username=request.data.get("username"),
            password=request.data.get("password"),
        )
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        return Response({"username": user.username})


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
