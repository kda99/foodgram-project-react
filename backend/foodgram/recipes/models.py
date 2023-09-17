from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
# from django.contrib.auth import get_user_model
import re

from django.db.models import UniqueConstraint

from users.models import User
# User = get_user_model()


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

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(

    )
    is_favorited = models.BooleanField(
        default=False,

    )
    is_in_shopping_cart = models.BooleanField(
        default=False,
    )
    name = models.CharField(
        'Название блюда',
        max_length=200,
        unique=True,
    )
    # image = models.ImageField(
    #     'Фото',
    #     upload_to='recipes/',
    # )
    text = models.TextField(
        'Описание',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления блюда в минутах',
        validators=[MinValueValidator(1, 'Время приготовления блюда должно'
                                         ' быть не менее 1 минуты'),],
    )
    pub_date = models.DateTimeField(
        'Дата рецепта',
        auto_now_add=True,
    )