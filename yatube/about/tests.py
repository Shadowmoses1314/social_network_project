from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from http import HTTPStatus


User = get_user_model()


class AboutPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()

    def test_auth_only_page(self):
        """страница об авторе, доступная неавторизованным пользователям."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_only_page(self):
        """страница о технологиях, доступная неавторизованным пользователям."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
