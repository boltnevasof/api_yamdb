from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from reviews.constants import NAME_LENGTH, SLUG_LENGTH
from reviews.utils import check_year_availability
from users.models import User


class Category(models.Model):
    # Модель для выбора категории произведения
    name = models.CharField('Название', max_length=NAME_LENGTH)
    slug = models.SlugField('Слаг', max_length=SLUG_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    # Модель для выбора жанра произведения
    name = models.CharField('Название', max_length=NAME_LENGTH)
    slug = models.SlugField('Слаг', max_length=SLUG_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    # Модель для хранения информации о произведении
    name = models.CharField('Название', max_length=NAME_LENGTH)
    year = models.PositiveIntegerField(
        'Год выхода',
        validators=(check_year_availability,)
    )
    description = models.TextField('Описание', blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
    )
    genre = models.ManyToManyField(Genre)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self) -> str:
        return self.name


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
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            )
        ]
        # сначала новые
        ordering = ['-pub_date']

    def __str__(self):
        return f'Отзыв {self.author} на {self.title}'


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
