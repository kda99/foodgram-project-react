from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django.utils.text import slugify
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filter import RecipeFilter
from api.permissions import IsAuthorOrSU
from api.serializers import (IngredientSerializer, PasswordSetSerializer,
                             RecipeCreateUpdateSerializer, RecipeSerializer,
                             RecipeSubscriptionsSerializer,
                             SubscriptionShowSerializer, TagSerializer,
                             UserCreateSerializer, UserGetSerializer)
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscription, User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ("retrieve", "create"):
            self.permission_classes = [
                permissions.AllowAny,
            ]
        return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        if self.action in ["set_password"]:
            return PasswordSetSerializer
        elif self.request.method == "GET":
            return UserGetSerializer
        elif self.request.method == "POST":
            return UserCreateSerializer

    def create(self, request, *args, **kwargs):
        password = request.data.get("password")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(password)
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        user = self.get_object()
        subscription = Subscription.objects.filter(
            user=request.user, author=user
        ).exists()
        if request.method == "POST":
            if user == request.user:
                return Response(
                    {"detail": "Нельзя подписаться на себя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not subscription:
                obj = Subscription.objects.create(
                    user=request.user, author=user)
                serializer = SubscriptionShowSerializer(
                    obj, context={"request": request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"detail": "Вы уже подписаны на этого автора."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if not subscription:
            return Response(
                {"detail": "Вы не подписаны на этого автора."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscription.objects.filter(user=request.user, author=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=("GET",),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(
            user=request.user).prefetch_related("author")
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionShowSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionShowSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # filter_backends = (DjangoFilterBackend,)
    # search_fields = ("^name",)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    # filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ("retrieve", "list"):
            self.permission_classes = [
                permissions.AllowAny,
            ]
        return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def handle_favorite_or_cart(
            self,
            request,
            model_class,
            error_message_post,
            error_message_delete,
            pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        obj = model_class.objects.filter(user=user, recipe=recipe)
        if request.method == "POST":
            if obj.exists():
                return Response(
                    {"error": error_message_post},
                    status=status.HTTP_400_BAD_REQUEST)
            model_class.objects.create(user=user, recipe=recipe)
            serializer = RecipeSubscriptionsSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not obj.exists():
            return Response(
                {"error": error_message_delete},
                status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        # permission_classes=(IsAuthorOrSU,),
        # permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        return self.handle_favorite_or_cart(
            request=request,
            model_class=Favorite,
            error_message_post="Рецепт уже в избранном.",
            error_message_delete="Рецепта нет в избранном.",
            pk=pk,
        )

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        # permission_classes=(IsAuthorOrSU,),
        # permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        return self.handle_favorite_or_cart(
            request=request,
            model_class=Cart,
            error_message_post="Рецепт уже в корзине.",
            error_message_delete="Рецепта нет в корзине.",
            pk=pk,
        )

    @action(
        detail=False,
        methods=("GET",),
        permission_classes=(IsAuthorOrSU,),
        # permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects.filter(recipe__carts__user=user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        content = "Список покупок:\n\n"
        for ingredient in ingredients:
            name = ingredient["ingredient__name"]
            amount = ingredient["total_amount"]
            unit = ingredient["ingredient__measurement_unit"]
            content += f"{name} - {amount} {unit}\n"
        filename = "Cart.txt"
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = (
            f"attachment;" f" filename={slugify(filename)}"
        )
        return response
