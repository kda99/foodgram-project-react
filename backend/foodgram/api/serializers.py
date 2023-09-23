from rest_framework import serializers

from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient
from users.models import User

from drf_extra_fields.fields import Base64ImageField


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class TagIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientCreateRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AuthorRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')
    author = AuthorRecipeSerializer()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(),)
    ingredients = IngredientCreateRecipeSerializer(many=True, source='recipe_ingredients', read_only=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',)


        