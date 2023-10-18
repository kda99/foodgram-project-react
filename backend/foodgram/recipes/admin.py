from django.contrib import admin

from recipes.models import Cart, Favorite, Recipe, RecipeIngredient, Tag


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


# @admin.register(Ingredient)
# class IngredientAdmin(admin.ModelAdmin):
#     list_display = (
#         "name",
#         "measurement_unit",
#     )
#     search_fields = ("name",)
#     list_filter = ("name", "measurement_unit")


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
