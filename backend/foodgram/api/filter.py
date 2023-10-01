from django_filters import rest_framework

from recipes.models import Recipe, Cart, Favorite, Tag


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.BooleanFilter(
        method='get_favorited_filter'
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='get_shopping_cart_filter'
    )
    author = rest_framework.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def get_favorited_filter(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__author=self.request.user)
        return queryset

    def get_shopping_cart_filter(self, queryset, name, value):
        if value:
            return queryset.filter(cart__author=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')