from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache
from http import HTTPStatus

from posts.models import Group, Post, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.create_url = '/create/'
        cls.post_url = f'/posts/{cls.post.id}/'
        cls.model_spec = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{cls.group.slug}/',
            'posts/profile.html': f'/profile/{cls.user.username}/',
            'posts/post_detail.html': cls.post_url,
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='no_name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_public_pages(self):
        """страницы, доступные всем."""
        for address in self.model_spec.values():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_autorized_only_page(self):
        """страница, доступная авторизованным пользователям."""
        response = self.authorized_client.get(self.create_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_only_page(self):
        """страница, доступная авторизованным пользователям."""
        response = self.guest_client.get(self.create_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_author_only_page(self):
        """страница редактирования поста, доступная только автору."""
        response = self.authorized_client.get(f"/posts/{self.post.id}/edit/")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        self.model_spec['posts/create_post.html'] = self.create_url
        for template, address in self.model_spec.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        """запрос к несуществующей странице."""
        response = self.guest_client.get('/somethingstrange/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_guest_post_create_url(self):
        """Страница по адресу /create/ ананим редирект в логин"""
        response = self.guest_client.get(
            reverse('posts:post_create'), follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/', HTTPStatus.FOUND)
