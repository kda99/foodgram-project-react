from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    search_fields = ("name",)
    list_filter = ("author", "name", "tags")
    list_display_links = ("name",)
    inlines = [
        RecipeIngredientInline,
    ]


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient
    # Перечислите поля модели, которые вы хотите импортировать из файла CSV
        fields = ('name', 'measurement_unit',)

    def import_id_fields(self):
        return []


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "user",
    )
    search_fields = ("recipe",)
    list_filter = ("recipe", "user")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "user",
    )
    search_fields = ("recipe",)
    list_filter = ("recipe", "user")
