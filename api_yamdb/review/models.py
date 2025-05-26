from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from titles.models import Title # Модель произ. к которому оставляют отзывы (еще не создано)

User = get_user_model()


class Review(models.Model):
    # модель отзыва на произведение 
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews' # Позволяет получить все отзывы через title.reviews.all()
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
