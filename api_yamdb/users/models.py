from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from reviews.constants import USERNAME_LENGTH

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)
REGEX_USERNAME = r'^[\w.@+-]+\Z'


class User(AbstractUser):
    # Модель пользователя

    # Переделанный username с валидатором на маску и me

    username = models.CharField(
        'Никнейм',
        max_length=USERNAME_LENGTH,
        unique=True,
        help_text='Обязательно. 150 символов или меньше. Только буквы,'
                  'цифры и @/./+/-/_',
        validators=[
            RegexValidator(
                regex=REGEX_USERNAME,
                message='Введите правильное имя пользователя.',
                code='invalid_username'
            ),
        ],
    )
    email = models.EmailField(
        'Имейл',
        max_length=254,
        unique=True,
        help_text='Обязательно. Электронная почта, максимум 254 символа.'
    )
    first_name = models.CharField(
        'Имя',
        max_length=USERNAME_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    # Выбор роли из трех возможных
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
    )
    # Код подтверждения аккаунта
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=255,
        null=True,
        blank=False,
        default='0000'
    )

    # Аттрибут проверки на юзера
    @property
    def is_user(self):
        return self.role == 'user'

    # Аттрибут проверки на админа
    @property
    def is_admin(self):
        return self.role == 'admin'

    # Аттрибут проверки на модератора
    @property
    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username
