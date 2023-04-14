from django.db import models
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        """
        Установка первоначальных данных в бд для тестирования
        """
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username="HasNoName")
        groupt = Group.objects.create(
            title="2",
            slug="2",
            description="2",
        )
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.po = Post(
            text=models.TextField(verbose_name="132", help_text="132"),
            pub_date=models.DateTimeField(auto_now_add=True),
            author=self.user,
            group=groupt,
        )
        self.po.save()

        # ещё пользователя (не автора поста), чтобы была проверка на
        # запрет к редактированию не автора поста
        self.user2 = User.objects.create_user(username="HasNoName2")
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_homepage(self):
        """
        Проверка доступности домашней страницы всем
        """
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_grouppage(self):
        """
        Проверка доступности странцы с группой всем
        """
        response = self.guest_client.get("/group/2/")
        self.assertEqual(response.status_code, 200)

    def test_profilepage(self):
        """
        Проверка доступности профиля всем
        """
        response = self.guest_client.get("/profile/HasNoName/")
        self.assertEqual(response.status_code, 200)

    def test_postspage(self):
        """
        Проверка доступности поста для всех
        """
        response = self.guest_client.get("/posts/1")
        self.assertEqual(response.status_code, 200)

    def test_editpage_worng_user(self):
        """
        Проверка на  не доступность редактирования для авторизированного пользователя
        не автора поста
        """
        response = self.authorized_client2.get("/posts/1/edit/")
        self.assertEqual(response.status_code, 302)

    def test_editpage_correct_user(self):
        """
        Проверка на доступность редактирования для авторизированного пользователя
        автора поста
        """
        response = self.authorized_client.get("/posts/1/edit/")
        self.assertEqual(response.status_code, 200)

    def test_createpage(self):
        """
        Проверка на доступность (код 200) создания постов для авторизированных
        """
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, 200)

    def test_unexistingpage(self):
        """
        Проверка на недоступность (ошибка 404) для всех клиентов
        """
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, 404)
