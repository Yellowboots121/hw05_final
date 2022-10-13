from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_post(self):
        post = PostModelTest.post
        self.assertEqual(post.text, str(post))

    def test_models_group(self):
        group = PostModelTest.group
        self.assertEqual(group.title, str(group))

    def test_models_verbose_name(self):
        post = PostModelTest.post
        verbose = post._meta.get_field('author').verbose_name
        self.assertEqual(verbose, 'Автор')

    def test_models_help_text(self):
        post = PostModelTest.post
        help_text = post._meta.get_field('group').help_text
        self.assertEqual(help_text, 'Группа, к которой будет относиться пост')
