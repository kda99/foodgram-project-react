from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.serializers import TagSerializer, RecipeSerializer, RecipeIngredientSerializer, PasswordSetSerializer, UserCreateSerializer, RecipeCreateSerializer, IngredientSerializer, UserSubscripterSeralizer, SubscriptionShowSerializer, RecipeSubscriptionsSerializer, UserGetSerializer
from recipes.models import Tag, Recipe, Ingredient, Favorite, RecipeIngredient
from users.models import User, Subscription
from api.pagination import CustomPagination
from api.filter import RecipeFilter


# class UserSubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     # permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = SubscriptionShowSerializer
#
#     def get_queryset(self):
#         return Subscription.objects.filter(user=self.request.user)
#
#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         page = self.paginate_queryset(queryset)
#
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)


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


    @action(detail=False, methods=['GET'])
    def subscriptions(self, request, pk=None):
        # Логика для получения подписок пользователя
        user = self.get_object()
        subscriptions = Subscription.objects.filter(user=user)
        serializer = SubscriptionShowSerializer(subscriptions, many=True)
        return Response(serializer.data)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer



class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
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

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        # url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        cart = Cart.objects.filter(
            user=user,
            recipe=recipe
        )
        if request.method == 'POST':
            if cart.exists():
                error = {
                    'errors':
                        'Рецепт уже в корзине.'
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            Cart(
                user=user,
                recipe=recipe
            ).save()
            serializer = RecipeSubscriptionsSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not cart.exists():
            error = {
                'errors':
                    'Этого рецепта нет в корзине.'
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',),
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__cart__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount',
        ).annotate(
            total_amount=Sum('amount')
        )
        list = []
        for ingredient in ingredients:
            list.append(
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
            )
        content = 'Список покупок:\n\n' + '\n'.join(list)
        filename = 'Cart.txt'
        request = HttpResponse(content, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request
