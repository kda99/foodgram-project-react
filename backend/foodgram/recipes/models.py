from django.db import models
from django.core.exceptions import ValidationError
import re

from django.db.models import UniqueConstraint


def validate_hex_color(value):
    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if not re.match(pattern, value):
        raise ValidationError('Неверный формат цвета. Цвет должен быть в формате HEX: #FFFFFF')


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        'Цвет тега',
        max_length=7,
        unique=True,
        validators=[validate_hex_color],
    )
    slug = models.SlugField(
        'Слаг тега',
        max_length=200,
        unique=True,
    )
    class Meta:
        ordering = ['id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            UniqueConstraint(fields=['name', 'slug'],
                             name='unique_tag')
        ]


