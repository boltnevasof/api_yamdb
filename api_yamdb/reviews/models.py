import datetime as dt

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class Category(models.Model):
    # Модель для выбора категории произведения
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField('Слаг', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    # Модель для выбора жанра произведения
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField('Слаг', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    # Модель для хранения информации о произведении
    name = models.CharField('Название', max_length=256)
    year = models.PositiveSmallIntegerField(
        'Год выхода',
        validators=[
            MaxValueValidator(dt.datetime.now().year),
        ],
    )
    description = models.TextField('Описание', blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
    )
    genre = models.ManyToManyField(Genre, through='TitleGenre')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self) -> str:
        return self.name


class TitleGenre(models.Model):
    # Промежуточная модель для хранения ключей genre и title
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, null=True, verbose_name='Жанр'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name='Произведение'
    )

    def __str__(self) -> str:
        return f'{self.title} - {self.genre}'


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
