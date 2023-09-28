from django.shortcuts import render, HttpResponse, get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.serializers import TagSerializer, RecipeSerializer, PasswordSetSerializer, UserCreateSerializer, RecipeCreateSerializer, IngredientSerializer, UserSubscripterSeralizer, SubscriptionShowSerializer, RecipeSubscriptionsSerializer, UserGetSerializer
from recipes.models import Tag, Recipe, Ingredient, Favorite
from users.models import User, Subscription
from api.pagination import CustomPagination



class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination


    def get_serializer_class(self):

        if self.action in ['set_password']:
            return PasswordSetSerializer

        elif self.request.method == 'GET':

            return UserGetSerializer

        elif self.request.method == 'POST':

            return UserCreateSerializer


    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        users = User.objects.filter(
            followed__user=request.user
        ).prefetch_related('recipes')
        page = self.paginate_queryset(users)

        if page is not None:
            serializer = UserSubscripterSeralizer(
                page, many=True,
                context={'request': request})

            return self.get_paginated_response(serializer.data)

        serializer = UserSubscripterSeralizer(
            users, many=True, context={'request': request}
        )

        return Response(serializer.data)

    @action(
        ["POST", "DELETE"],
        detail=True,
    )
    def subscribe(self, request, **kwargs):
        user = get_object_or_404(User, id=kwargs.get('id'))
        subscription = Subscription.objects.filter(
            user=request.user,
            author=user
        )
        if request.method == 'POST':
            if user == request.user:
                error = {
                    'errors': 'Нельзя подписаться на себя.'
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            obj, created = Subscription.objects.get_or_create(
                user=request.user,
                author=user
            )
            if not created:
                error = {
                    'errors': 'Вы уже подписаны на этого автора'
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionShowSerializer(obj, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not subscription:
            error = {
                'errors': 'Вы не подписаны на этого автора.'
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer



class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
    )
    def favorite(self, request, pk  = None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = Favorite.objects.filter(
            user=user,
            recipe=recipe
        )
        if request.method == 'POST':
            if favorite.exists():
                error = {
                    'errors': 'Рецепт уже в избранном.'
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            Favorite(
                user=user,
                recipe=recipe
            ).save()
            serializer = RecipeSubscriptionsSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not favorite.exists():
            error = {'errors': 'Рецепта нет в избранном.'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

