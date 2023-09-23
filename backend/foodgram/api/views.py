from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet

from api.serializers import TagSerializer, RecipeSerializer, RecipeCreateSerializer, IngredientSerializer
from recipes.models import Tag, Recipe, Ingredient


class CustomUserViewSet(UserViewSet):
    pass


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
