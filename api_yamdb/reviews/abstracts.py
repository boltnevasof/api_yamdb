from django.db import models
from reviews.constants import NAME_LENGTH, SLUG_LENGTH


class BaseNameSlugModel(models.Model):
    # Абстрактная базовая модель с полями name и slug
    name = models.CharField('Название', max_length=NAME_LENGTH)
    slug = models.SlugField('Слаг', max_length=SLUG_LENGTH, unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name
