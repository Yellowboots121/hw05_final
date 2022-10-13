from http import HTTPStatus
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.not_author = User.objects.create_user(username='no_author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст нвого поста',
        )
        cls.authorized_client_not_author = Client()
        cls.authorized_client_not_author.force_login(cls.not_author)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='Batman')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_and_group(self):
        """страницы группы и главная доступны всем"""
        url_names = (
            '/',
            '/group/test_slug/',
            '/profile/test_user/',
            f'/posts/{self.post.pk}/',
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_for_authorized(self):
        """Страница /create доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_url(self):
        """без авторизации приватные URL недоступны"""
        url_names = (
            '/create/',
            f'/posts/{self.post.pk}/edit/',
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_redirect_anonymous_on_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/')
        url = urljoin(reverse('login'), "?next=/create/")
        self.assertRedirects(response, url)

    def test_no_author_of_post_cant_edit_post(self):
        """Страница posts/<post_id>/edit/ не доступна
         авторизованному пользователю, но не автору поста"""
        response = self.authorized_client_not_author.get(
            f'/posts/{self.post.pk}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.pk}/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unknown_page_url_unexists_at_desired_location(self):
        """Страница не существует"""
        response = Client().get('/none/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/create_post.html': '/create/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
            'posts/profile.html': '/profile/test_user/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
