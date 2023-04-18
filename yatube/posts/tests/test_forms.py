import shutil
import tempfile

from posts.forms import PostCreateForm
from posts.models import Post
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            title='Тестовый заголовок',
            text='Тестовый текст',
            group='Тестовая группа'
        )
        cls.form = PostCreateForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='img/gif'
        )
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый тест',
            'image': uploaded,
        }
        response = self.guest_client.post(
            reverse('posts:creat_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:post_edit'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                image='posts/small.gif',
            ).exists()
        )

    def test_cant_create(self):
        posts_count = Post.objects.count()
        form_data = {
            'title': 'Заголовок из формы',
            'text': 'Текст из формы'
        }
        response = self.guest_client.post(
            reverse('posts:post_edit'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(
            response,
            'form'
        )
        self.assertEqual(response.status_code, 200)
