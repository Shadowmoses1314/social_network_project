from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from posts.models import Group, Post

User = get_user_model()


class PostAndGroupModelTest(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.post_url = f'/{cls.user.username}/{cls.post.id}/'

        cls.public_urls = (
            ('/', 'index.html'),
            (f'/group/{cls.group.slug}/', 'group.html'),
            (f'/{cls.user.username}/', 'profile.html'),
            (cls.post_url, 'post.html'),
        )

    def test_models_have_correct_object_names_posts(self):
        """Проверяем, что у Post корректно работает __str__."""
        post = PostAndGroupModelTest.post
        expected_object_name = post.text
        self.assertEqual(str(post), expected_object_name)

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у Group корректно работает __str__."""
        group = PostAndGroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(str(group), expected_object_name)
