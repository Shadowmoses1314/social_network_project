from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, Follow

User = get_user_model()

PAGE_2 = '?page=2'

POSTS_INDEX = 'posts:index'


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_name')
        cls.group = Group.objects.create(
            title='Тест',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse(POSTS_INDEX),

            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={
                    'slug': PostPagesTests.group.slug})
            ),

            'posts/profile.html': (
                reverse('posts:profile', kwargs={
                    'username': PostPagesTests.user.username})
            ),

            'posts/create_post.html': reverse('posts:post_create'),

            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={
                    'post_id': PostPagesTests.post.id})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PostContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_name')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
            description='Тестовое',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):

        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostContextTests.user)

    def post_context_check(self, response):
        response = self.authorized_client.get(reverse(POSTS_INDEX))
        self.assertIn('page_obj', response.context)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author.username, self.user.username),
        self.assertEqual(first_object.text, 'Тестовый текст'),
        self.assertEqual(first_object.group, self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон профайл сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.post_context_check(response)


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_name')
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug='test_slug',
            description='описание',
        )
        cls.bulk_list = []
        for cls.count_post in range(13):
            cls.post = Post(
                text=f'Тестовый текст {cls.count_post}',
                author=cls.user,
                group=cls.group
            )
            cls.bulk_list.append(cls.post)
        Post.objects.bulk_create(cls.bulk_list)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        paginator_list = {
            'posts:index': reverse(POSTS_INDEX),
            'posts:group_list': reverse(
                'posts:group_list', kwargs={
                    'slug': PostPaginatorTests.group.slug}),
            'posts:profile': reverse(
                'posts:profile', kwargs={
                    'username': PostPaginatorTests.user.username}),
        }
        for reverse_name in paginator_list.values():
            response = self.guest_client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_ten_posts(self):
        paginator_list = {
            'posts:index': reverse('posts:index',) + PAGE_2,
            'posts:group_list': reverse(
                'posts:group_list', kwargs={
                    'slug': PostPaginatorTests.group.slug}) + PAGE_2,
            'posts:profile': reverse(
                'posts:profile', kwargs={
                    'username': PostPaginatorTests.user.username}) + PAGE_2,
        }
        for reverse_name in paginator_list.values():
            response = self.guest_client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), 3)

    def test_cache(self):
        """Проверяем, что кэш работает"""
        response_1 = self.client.get(reverse(POSTS_INDEX)).content
        Post.objects.all().delete
        response_2 = self.client.get(reverse(POSTS_INDEX)).content
        self.assertEqual(response_1, response_2)
        Post.objects.all().delete
        cache.clear()
        response_3 = self.client.get(reverse(POSTS_INDEX)).content
        self.assertNotEqual(response_1, response_3)


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
        пользователей и удалять подписки'''
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
        response_nonfollower = self.nonfollower_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(
            len(response_nonfollower.context['page_obj']),
            0
        )
