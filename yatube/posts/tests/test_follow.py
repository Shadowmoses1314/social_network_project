from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post

User = get_user_model()


class PostFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Author')
        cls.follower = User.objects.create(username='Follower')
        cls.nonfollower = User.objects.create(username='Nonfollower')

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.nonfollower_client = Client()
        self.nonfollower_client.force_login(self.nonfollower)
        cache.clear()

    def test_follow_and_unfollow(self):
        '''Авторизованный пользователь может подписываться на других
        пользователей и удалять '''
        self.follower_client.get(
            (reverse('posts:profile_follow', kwargs={'username': 'Author'})),
        )
        self.assertEqual(
            Follow.objects.filter(
                user=self.follower,
            ).count(),
            1,
        )
        self.follower_client.get(
            (reverse('posts:profile_unfollow', kwargs={'username': 'Author'})),
        )
        self.assertEqual(
            Follow.objects.filter(user=self.follower).count(),
            0
        )

    def test_follow_index(self):
        '''Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан.'''
        Post.objects.create(
            author=self.author,
            text='Тестовый пост',
        )
        Follow.objects.create(
            user=self.follower, author=self.author
        )
        response_follower = self.follower_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(
            len(response_follower.context['page_obj']),
            1
        )
        # cache.clear()
        response_nonfollower = self.nonfollower_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(
            len(response_nonfollower.context['page_obj']),
            0
        )
