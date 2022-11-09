from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class ViewTestClass(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_name')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_urls_404(self):
        url_clients = {
            self.guest_client: '/fakeurl',
            self.authorized_client: '/fakeurl',
        }
        for client, url in url_clients.items():
            with self.subTest(client=client):
                response = client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
