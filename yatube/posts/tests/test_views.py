from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post
from http import HTTPStatus
User = get_user_model()


class PostPagesTests(TestCase):
    """Тестирование страниц во вью-функциях в приложении Posts"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='Something'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
​
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        И проверяем, что при обращении к name вызывается
        соответствующий HTML-шаблон.
        """
        templates_page_names = {
            'posts/index.html': reverse('index'),
            'posts/post_create.html': reverse('post_create'),
            'posts/group_list.html': (
                reverse('group_posts', kwargs={'slug': 'test_slug'})
            ),
            'posts/profile.html': reverse('profile'),
            'posts/post_detail.html': reverse('post_detail')
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
    
    def test_post_edit_uses_correct_template(self):
        response = self.authorized_client.get('posts:post_edit', kwargs={'post_id': id})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/post_create.html')
    
    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_author_0, 'auth')

    def test_new_post_show_correct_context(self):
        response = self.authorized_client.get(reverse('post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@mail.ru',
                                              password='test_pass',)
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug2',
            description='Тестовое описание')
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='mob2556')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        list_urls = {
            reverse("index"): "index",
            reverse("group_list", kwargs={"slug": "test_slug2"}): "group",
            reverse("profile", kwargs={"username": "test_name"}): "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_posts(self):
        list_urls = {
            reverse("index") + "?page=2": "index",
            reverse("group_list", kwargs={"slug": "test_slug2"}) + "?page=2":
            "group",
            reverse("profile", kwargs={"username": "test_name"}) + "?page=2":
            "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context.get('page').object_list), 3)
