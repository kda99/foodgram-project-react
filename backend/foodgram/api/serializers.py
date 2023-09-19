from rest_framework import serializers

from recipes.models import Tag, Recipe, RecipeIngredient
from users.models import User

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


# class AuthorRecipeSerializer(serializers.ModelSerializer):
#     name
#     class Meta:
#         model = User
#         fields = ('id', 'name', 'image')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')
    # author = AuthorRecipeSerializer()

    class Meta:
        model = Recipe
        fields = '__all__'