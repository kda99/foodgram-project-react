import re
from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
# from django.contrib.auth import get_user_model

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
        return str(self.name)


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
        unique=True,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(fields=['name', 'measurement_unit'],
                             name='unique_ingredient')
        ]

    def __str__(self):
        return str(self.name) + ' ' + str(self.measurement_unit)


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
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
        through='RecipeIngredient',
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
    image = models.ImageField(
        'Фото',
        upload_to='recipes/',
    )
    text = models.TextField(
        'Описание',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления блюда в минутах',
        validators=[MinValueValidator(1, 'Время приготовления блюда должно'
                                         ' быть не менее 1 минуты'), ],
    )
    pub_date = models.DateTimeField(
        'Дата рецепта',
        auto_now_add=True,
    )


    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            UniqueConstraint(fields=['name', 'author'], name='unique_recipe'),
        ]
    def __str__(self):
        return str(self.name)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(1, 'Количество не может быть меньше 1')],
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Количество ингредиента в рецепте'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        related_name='favorites',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user', ),
                name='unique_favorite',
            ),
        )

    def __str__(self):
        return str(self.recipe.name)


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='cart',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
            )
    recipe = models.ForeignKey(
        Recipe,
        related_name='cart',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_cart',
            ),
        )

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
