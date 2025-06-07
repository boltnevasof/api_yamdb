from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from reviews.constants import (CONFIRMATION_CODE_LENGTH, EMAIL_LENGTH,
                               FIRSTNAME_LENGTH, LASTNAME_LENGTH, ROLE_LENGTH,
                               USERNAME_LENGTH)

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'
REGEX_USERNAME = r'^[\w.@+-]+\Z'


class RoleChoices(models.TextChoices):
    USER = USER, 'Пользователь'
    ADMIN = ADMIN, 'Администратор'
    MODERATOR = MODERATOR, 'Модератор'


class User(AbstractUser):
    # Модель пользователя

    # Переделанный username с валидатором на маску

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
        max_length=EMAIL_LENGTH,
        unique=True,
        help_text='Обязательно. Электронная почта, максимум 254 символа.'
    )
    first_name = models.CharField(
        'Имя',
        max_length=FIRSTNAME_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=LASTNAME_LENGTH,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    # Выбор роли из трех возможных
    role = models.CharField(
        'Роль',
        max_length=ROLE_LENGTH,
        choices=RoleChoices.choices,
        default=RoleChoices.USER,
    )
    # Код подтверждения аккаунта
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=CONFIRMATION_CODE_LENGTH,
        blank=False,
        default='0000'
    )
    is_superuser = models.BooleanField(
        'Является суперюзером',
        default=False
    )
    is_staff = models.BooleanField(
        'Является персоналом',
        default=False
    )

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR or self.is_superuser or self.is_staff

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username
