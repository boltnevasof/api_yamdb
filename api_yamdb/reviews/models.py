from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser

# Модель произ. к которому оставляют отзывы (еще не создано)
from titles.models import Title


class User(AbstractUser):
    # модель пользователя

    # переделанный username с валидатором с маской как в redoc
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Обязательно. 150 символов или меньше. Только буквы,'
                  'цифры и @/./+/-/_',
        validators=[
            models.validators.RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Введите правильное имя пользователя.',
                code='invalid_username'
            ),
        ],
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        help_text='Обязательно. Электронная почта, максимум 254 символа.'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )
    bio = models.TextField(
        blank=True,
        null=True
    )
    # возможные роли и их читаемый вид
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]
    # выбор роли из трех возможных
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
    )

    def __str__(self):
        return self.username


class Review(models.Model):
    # модель отзыва на произведение
    title = models.ForeignKey(
        # Позволяет получить все отзывы через title.reviews.all()
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    # Текс отзыва
    text = models.TextField()
    # Автор отзыва (пользователь)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    # оценка от 1 до 10
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    # дата публикации
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # один пользователь оставляет один отзыв
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]
        # сначала новые
        ordering = ['-pub_date']

    def __str__(self):
        return f'{self.author} — {self.title}'


class Comment(models.Model):
    # привязка комента к отзыву
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return f'{self.author}: {self.text[:30]}'
