# (venv) ~/django-projects/Mac $ python manage.py makemigrations
# (venv) ~/django-projects/Mac $ python manage.py migrate
# (venv) ~/django-projects/Mac $ python manage.py shell


from django.db import models
from django.contrib.auth.models import User


from django.urls import reverse
from datetime import datetime

from django.contrib.auth.forms import UserCreationForm
from django import forms

from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

from django.core.mail import send_mail
from django.template.loader import render_to_string




class CommonSignupForm(SignupForm):
    def save(self, request):
        user = super(CommonSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)

        activation_link = request.build_absolute_uri(reverse('activate', args=[user.pk, user.activation_key]))

        # приветственное письмо пользователю
        subject = 'Добро пожаловать в новостной портал'
        message = f'Спасибо за регистрацию на сайте: {user.username}!'
        html_message = render_to_string('welcome_email.html', {'user': user, 'activation_link': activation_link})
        from_email = 'poc47a.t@yandex.ru'  # адрес электронной почты
        recipient_list = [user.email]
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        return user

class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label = "Email")
    first_name = forms.CharField(label = "Имя")
    last_name = forms.CharField(label = "Фамилия")


    class Meta:
        model = User
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2",

        )


# Модель, содержащая объекты всех авторов.
# cвязь «один к одному» с встроенной моделью пользователей User;
class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    username = models.CharField(max_length=255, unique=True)
    #рейтинг пользователя. Ниже будет дано описание того, как этот рейтинг можно посчитать.
    def update_rating(self):
        post_rating = sum(self.news.all().values_list('rating', flat=True))
        comment_rating = sum(self.user.comments.all().values_list('rating', flat=True))
        self.rating = post_rating * 3 + comment_rating
        self.save()

    def __str__(self):
        return self.username

# Категории новостей/статей — темы, которые они отражают (спорт, политика, образование и т. д.).
# Имеет единственное поле: название категории. Поле должно быть уникальным
# (в определении поля необходимо написать параметр unique = True).
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories', blank=True)

    def __str__(self):
        return self.name


# Новости
class News(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True, # названия новостей не должны повторяться

    )

    description = models.TextField()

    # поле категории будет ссылаться на модель категории
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        related_name='news', # все новости в категории будут доступны через поле news
    )

    published_date = models.DateTimeField(default=datetime.now)  # предоставляем значение по умолчанию

    author = models.CharField(max_length=100, default='нет автора')

    def send_newsletter(self):
        subject = self.name
        from_email = 'poc47a.t@yandex.ru'
        for user in self.category.subscribers.all():
            html_message = render_to_string('newsletter.html', {'news': self, 'user': user})
            message = f"Здравствуйте, {user.username}. Новая статья в твоём любимом разделе! {self.name}: {self.description[:50]}"
            send_mail(
                subject,
                message,
                from_email, # здесь указываете почту, с которой будете отправлять (об этом попозже) ,
                #recipient_list=[]  # здесь список получателей. Например, секретарь, сам врач и т. д.
                [user.email],
                html_message=html_message,
                fail_silently=False
            )


    def __str__(self):
        return f'{self.name.title()}: {self.description[:20]}: {self.published_date}: {self.author} '

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])


# Эта модель должна содержать в себе статьи и новости, которые создают пользователи.
# Каждый объект может иметь одну или несколько категорий.
# Соответственно, модель должна включать следующие поля:
# связь «один ко многим» с моделью Author;
# поле с выбором — «статья» или «новость»;
# автоматически добавляемая дата и время создания;
# связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory);
# заголовок статьи/новости;
# текст статьи/новости;
# рейтинг статьи/новости.
class Post(models.Model):
    POST_TYPES = (
        ('article', 'Article'),
        ('news', 'News')
    )
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=7, choices=POST_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def update_rating(self):
        self.rating = self.likes.all().count() - self.dislikes.all().count()
        self.save()
        self.author.update_rating()

    def preview(self):
        if len(self.text) > 127:
            return self.text[:124] + '...'
        else:
            return self.text

    def __str__(self):
        return self.title

# Промежуточная модель для связи «многие ко многим»:
# связь «один ко многим» с моделью Post;
# связь «один ко многим» с моделью Category.
class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


# Под каждой новостью/статьёй можно оставлять комментарии, поэтому необходимо организовать их способ хранения тоже.
# Модель будет иметь следующие поля:
# связь «один ко многим» с моделью Post;
# связь «один ко многим» со встроенной моделью User (комментарии может оставить любой пользователь, необязательно автор);
# текст комментария;
# дата и время создания комментария;
# рейтинг комментария.
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        self.rating = self.likes.all().count() - self.dislikes.all().count()
        self.save()
        self.post.update_rating()
        self.user.author.update_rating()

    def like(self):
        self.rating += 1
        self.save()
        self.update_rating()

    def dislike(self):
        self.rating -= 1
        self.save()
        self.update_rating()

    def __str__(self):
        return self.text

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

class Dislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='dislikes')
