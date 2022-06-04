from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group


class BaseAPITestCase(APITestCase):

    def setUp(self) -> None:
        Group.objects.create(name="editor")
        return super().setUp()

    def _register_and_login(self, username, password):
        response = self.client.post(
            reverse("register"),
            {"username": username, "password": password},
        )
        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username=username)
        user.is_active = True
        user.save()

        response = self.client.login(username=username, password=password)
        self.assertTrue(response)

        return username

    def fake_user(self, username="user1"):
        return self._register_and_login(username, "password")

    def fake_admin(self):
        return self._register_and_login("admin", "password")

    def logout(self):
        self.client.get(reverse("logout"))
        self.client.credentials()
