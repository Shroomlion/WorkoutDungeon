from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthFlowTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="hero", password="hunter22")

    def test_login_success_establishes_session(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "hero", "password": "hunter22"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "hero")
        # Session cookie should now grant access to protected endpoints.
        me = self.client.get("/api/characters/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)

    def test_login_bad_password_rejected(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "hero", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_clears_session(self):
        self.client.post(
            "/api/auth/login/",
            {"username": "hero", "password": "hunter22"},
            format="json",
        )
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        me = self.client.get("/api/characters/me/")
        self.assertEqual(me.status_code, status.HTTP_403_FORBIDDEN)

    def test_csrf_endpoint_sets_cookie(self):
        response = self.client.get("/api/auth/csrf/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("csrftoken", response.cookies)
