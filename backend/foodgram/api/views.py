from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django.utils.text import slugify
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from api.serializers import TagSerializer, RecipeSerializer, RecipeIngredientSerializer, PasswordSetSerializer, UserCreateSerializer, RecipeCreateSerializer, IngredientSerializer, UserSubscripterSeralizer, SubscriptionShowSerializer, RecipeSubscriptionsSerializer, UserGetSerializer
from recipes.models import Tag, Recipe, Ingredient, Favorite, RecipeIngredient, Cart
from users.models import User, Subscription
from api.filter import RecipeFilter


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = PageNumberPagination



    def get_serializer_class(self):

        if self.action in ['set_password']:
            return PasswordSetSerializer
        elif self.request.method == 'GET':
            return UserGetSerializer
        elif self.request.method == 'POST':
            return UserCreateSerializer

    def create(self, request, *args, **kwargs):
        password = request.data.get('password')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(password)  # Задаем пароль
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        user = self.get_object()
        subscription = Subscription.objects.filter(user=request.user, author=user).exists()
        if request.method == 'POST':
            if user == request.user:
                raise ValidationError('Нельзя подписаться на себя.')
            if not subscription:
                obj = Subscription.objects.create(user=request.user, author=user)
                serializer = SubscriptionShowSerializer(obj, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                raise ValidationError('Вы уже подписаны на этого автора.')
        if not subscription:
            raise ValidationError('Вы не подписаны на этого автора.')
        Subscription.objects.filter(user=request.user, author=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes = (permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user).prefetch_related('author')
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionShowSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionShowSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = DjangoFilterBackend,
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
    )
    def favorite(self, request, pk = None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if favorite.exists():
                raise ValidationError('Рецепт уже в избранном.')
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeSubscriptionsSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not favorite.exists():
            raise ValidationError('Рецепта нет в избранном.')
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        cart = Cart.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if cart.exists():
                raise ValidationError('Рецепт уже в корзине.')
            Cart.objects.create(user=user, recipe=recipe)
            serializer = RecipeSubscriptionsSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not cart.exists():
            raise ValidationError('Этого рецепта нет в корзине.')
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',),
    )
    def download_shopping_cart(self, request):

        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__carts__user=user).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(
            total_amount=Sum('amount')
        )
        ingredients_dict = {}
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            amount = ingredient['total_amount']
            unit = ingredient['ingredient__measurement_unit']
            if name in ingredients_dict:
                ingredients_dict[name]['total_amount'] += amount
            else:
                ingredients_dict[name] = {
                    'name': name,
                    'total_amount': amount,
                    'measurement_unit': unit,
                }
        content = 'Список покупок:\n\n'
        for ingredient in ingredients_dict.values():
            name = ingredient['name']
            amount = ingredient['total_amount']
            unit = ingredient['measurement_unit']
            content += f'{name} - {amount} {unit}\n'
        filename = 'Cart.txt'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={slugify(filename)}'
        return response
