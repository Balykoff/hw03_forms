from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.test import TestCase
from django.urls import reverse
from ..models import Post, Group

User = get_user_model()


class Test(TestCase):
    def setUp(self):
        """
        Установка первоначальных данных в бд для тестирования
        """
        #Задание 1-2-3
        self.guest_client = Client()
        self.user = User.objects.create_user(username="NonAuthUser")
        self.user2 = User.objects.create_user(username="NonAuthUser2")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title="Тестовая группа", slug="test_group")
        TEST_OF_POST = 14
        bilk_post = []
        for i in range(TEST_OF_POST):
            bilk_post.append(
                Post(text=f"Тестовый текст {i}", group=self.group, author=self.user)
            )
        Post.objects.bulk_create(bilk_post)

        self.group2 = Group.objects.create(title="Тестовая группа2", slug="test_group2")
        TEST_OF_POST2 = 17
        bilk_post2 = []
        for i in range(TEST_OF_POST, TEST_OF_POST + TEST_OF_POST2):
            bilk_post2.append(
                Post(text=f"Тестовый текст {i}", group=self.group2, author=self.user2)
            )
        Post.objects.bulk_create(bilk_post2)

        # Дополнительные данные для третьего задания
        self.group3 = Group.objects.create(title="Тестовая группа3", slug="test_group3")
        self.user3 = User.objects.create_user(username="NonAuthUser3")
        Post.objects.create(
            text=f"Третье задание группа 3 юзер 3", group=self.group3, author=self.user3
        )

    # Задание 1
    def test_index_template(self):
        """
        Проверка, что в функции index используется корректный шаблон
        """
        response = self.client.get(reverse("posts:index"))
        self.assertTemplateUsed(response, "posts/index.html")

    def test_group_template(self):
        """
        Проверка, что в функции group_list используется корректный шаблон
        """
        response = self.client.get(
            reverse("posts:group_list", kwargs={"slug": self.group2.slug})
        )
        self.assertTemplateUsed(response, "posts/group_list.html")

    def test_profile_template(self):
        """
        Проверка, что в функции profile используется корректный шаблон
        """
        response = self.client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        )
        self.assertTemplateUsed(response, "posts/profile.html")

    def test_post_template(self):
        """
        Проверка, что в функции post_detail используется корректный шаблон
        """
        response = self.client.get(reverse("posts:post_detail", kwargs={"post_id": 1}))
        self.assertTemplateUsed(response, "posts/post_detail.html")

    def test_post_create_template(self):
        """
        Проверка, что в функции post_create используется корректный шаблон
        """
        response = self.authorized_client.get(reverse("posts:create"))
        self.assertTemplateUsed(response, "posts/create_post.html")

    def test_post_edit_template(self):
        """
        Проверка, что в функции post_edit используется корректный шаблон
        """
        response = self.authorized_client.get(
            reverse("posts:edit", kwargs={"post_id": 1})
        )
        self.assertTemplateUsed(response, "posts/update_post.html")

    # Задание 2
    def test_index(self):
        """
        -Проверка что в индекс передаётся список из 32 постов
        -Проверка работы паджинатора
        """
        response1 = self.client.get(reverse("posts:index"))
        response2 = self.client.get(reverse("posts:index") + "?page=2")
        response3 = self.client.get(reverse("posts:index") + "?page=3")
        response4 = self.client.get(reverse("posts:index") + "?page=4")

        count_of_posts1 = len(response1.context["page_obj"])
        count_of_posts2 = len(response2.context["page_obj"])
        count_of_posts3 = len(response3.context["page_obj"])
        count_of_posts4 = len(response4.context["page_obj"])

        self.assertEqual(count_of_posts1, 10)
        self.assertEqual(count_of_posts2, 10)
        self.assertEqual(count_of_posts3, 10)
        self.assertEqual(count_of_posts4, 2)

    def test_goup_list(self):
        """
        -Проверка что в группу 2 передаётся 17 постов
        -Проверка работы паджинатора
        """
        response1 = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group2.slug})
        )
        response2 = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group2.slug}) + "?page=2"
        )

        count_of_posts1 = len(response1.context["page_obj"])

        count_of_posts2 = len(response2.context["page_obj"])

        self.assertEqual(count_of_posts1, 10)
        self.assertEqual(count_of_posts2, 7)

    def test_profile_list(self):
        """
        -Проверка что в профайл передаётся 14 постов
        -Проверка работы паджинатора
        """
        response1 = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        )
        response2 = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
            + "?page=2"
        )

        count_of_posts1 = len(response1.context["page_obj"])

        count_of_posts2 = len(response2.context["page_obj"])

        self.assertEqual(count_of_posts1, 10)
        self.assertEqual(count_of_posts2, 4)

    def test_post_detail(self):
        """
        Проверка поста отфильтрованного по id
        """
        response1 = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": 1})
        )
        self.assertEqual(str(response1.context["post"]), "Тестовый текст 0")

    def test_post_create_1(self):
        """
        Проверка формы редактирования поста
        """
        response1 = self.authorized_client.get(
            reverse("posts:edit", kwargs={"post_id": 1})
        )
        self.assertEqual(str(response1.context["is_edit"]), "True")

    def test_post_create_2(self):
        """
        Проверка формы создания поста
        """
        response1 = self.authorized_client.get(reverse("posts:create"))
        self.assertEqual(str(response1.context["is_edit"]), "False")

    # Задание 3
    def test_post_index(self):
        """
        Проверка что при создании, пост появляется на главной странице сайта
        """
        response1 = self.guest_client.get(reverse("posts:index"))
        self.assertTrue(
            "Третье задание группа 3 юзер 3" in str(response1.context["page_obj"][:])
        )

    def test_post_group(self):
        """
        Проверка что при создании, пост появляется на странице выбранной группы
        """
        response1 = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group3.slug})
        )
        self.assertTrue(
            "Третье задание группа 3 юзер 3" in str(response1.context["page_obj"][:])
        )

    def test_post_profile(self):
        """
        Проверка что при создании, пост появляется в профайле пользователя
        """
        response1 = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": self.user3.username})
        )
        self.assertTrue(
            "Третье задание группа 3 юзер 3" in str(response1.context["page_obj"][:])
        )

    def test_post_not_in_other_group(self):
        """
        Проверка что при создании, пост не попадёт в группу для которой не предназначен
        """
        response1 = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group2.slug})
        )
        self.assertFalse(
            "Третье задание группа 3 юзер 3" in str(response1.context["page_obj"][:])
        )
