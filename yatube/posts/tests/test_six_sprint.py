from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, Follow, Comment

User = get_user_model()


class SprintSixTest(TestCase):
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

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.user = User.objects.create_user(
            username='test_user',
        )
        self.follower = User.objects.create_user(
            username='testfollower',
        )
        self.following = User.objects.create_user(
            username='testfollowing',
        )
        self.authorized_client.force_login(self.user)

    def test_image(self):
        count_posts = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        img = SimpleUploadedFile(
            "small.gif",
            small_gif,
            content_type="image/gif"
        )
        post = Post.objects.create(
            text='Test post with img',
            author=self.user,
            group=self.group,
            image=img
        )
        urls = (
            reverse('posts:index'),
            reverse('posts:profile', args=[post.author.username]),
            reverse('posts:post_detail', args=[self.post.pk]),
            reverse('posts:group_list', args=[self.group.slug]),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(Post.objects.count(), count_posts + 1)

    def test_comments(self):
        self.text = 'Test comments'
        self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={
                'post_id': self.post.pk
            }),
            {'text': 'Comment'}
        )
        comment = self.post.comments.select_related('author').first()
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.text, 'Comment')
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name'),
            text='Тестовая запись')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Batman')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Тест кэширования страницы index.html"""
        first_state = self.authorized_client.get(reverse('posts:index'))
        post_1 = Post.objects.get(pk=1)
        post_1.text = 'Измененный текст'
        post_1.save()
        second_state = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first_state.content, second_state.content)
        cache.clear()
        third_state = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_state.content, third_state.content)


class FollowTests(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(username='follower',)
        self.user_following = User.objects.create_user(username='following',)
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовая запись'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.client_auth_follower.get(reverse('posts:profile_unfollow',
                                      kwargs={'username':
                                              self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)
