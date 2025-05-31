from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    # модель пользователя

    # переделанный username с валидатором с маской как в redoc
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Обязательно. 150 символов или меньше. Только буквы,'
                  'цифры и @/./+/-/_',
        validators=[
            RegexValidator(
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
