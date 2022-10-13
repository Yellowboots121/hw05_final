import shutil
import tempfile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from posts.models import Group, Post
User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name1'),
            text='Тестовая запись',
            group=Group.objects.create(
                title='Заголовок для тестовой группы',
                slug='test_slug'))

        cls.group = Group.objects.create(
            title='Лев Толстой',
            slug='test_slug10'
        )

        cls.author = User.objects.create_user(
            username='authorPosts')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Batman')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    def test_form_create(self):
        """Проверка создания нового поста, авторизированным пользователем"""
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тестовая запись',
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': 'Batman'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Тестовая запись',
            group=TestCreateForm.group).exists())

    def test_form_edit(self):
        """Проверка редактирования поста через форму на странице"""
        post_count = Post.objects.count()
        small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.jpg',
            content=small_jpg,
            content_type='image/jpg'
        )
        form_data = {
            'group': self.group.id,
            'text': 'Измененный текст',
            'image': uploaded,
        }
        response = self.authorized_author.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(
            text='Измененный текст',
            group=TestCreateForm.group).exists())
        self.assertEqual(Post.objects.count(), post_count)
        post = Post.objects.get(id=self.post.pk)
        self.assertEqual(post.text, 'Измененный текст')
