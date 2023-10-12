from collections import Counter

from django.db import transaction
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Cart, Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class TagIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id",)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed")

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request.user.is_authenticated:
            return False

        return Subscription.objects.filter(
            user=request.user, author=obj).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    author = UserGetSerializer(many=False, read_only=True)
    image = Base64ImageField(max_length=10485760)
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredients",
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "ingredients",
            "author",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def create_recipe_ingredients(self, recipe, ingredients):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get("id"),
                amount=ingredient.get("amount"),
            )
            for ingredient in ingredients
        ]
        with transaction.atomic():
            RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def validate(self, data):
        image = data.pop("image")
        data.pop("tags")
        tags = self.initial_data.get("tags")
        validated_data = super().validate(data)
        ingredients = self.initial_data.get("ingredients")
        ingredient_ids = [ingredient.get("id") for ingredient in ingredients]
        duplicate_ingredients = [
            ingredient for ingredient,
            count in Counter(ingredient_ids).items() if count > 1]
        if duplicate_ingredients:
            raise serializers.ValidationError(
                f"Найдены дубликаты для идентификаторов ингредиентов:"
                f" {duplicate_ingredients}"
            )
        validated_data["ingredients"] = ingredients
        validated_data["image"] = image
        validated_data["tags"] = tags
        return validated_data

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        self.create_recipe_ingredients(recipe=recipe, ingredients=ingredients)
        tag_ids = [tag for tag in tags_data]
        tags = Tag.objects.filter(id__in=tag_ids)
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        tags = instance.tags.all()
        tag_serializer = TagSerializer(tags, many=True)
        representation["tags"] = tag_serializer.data
        return representation

    def update(self, recipe, validated_data):
        recipe.ingredients.clear()
        recipe.tags.clear()
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.create_recipe_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)


class RecipeSubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class UserSubscripterSeralizer(serializers.ModelSerializer):
    """
    /api/users/subscriptions/?page=1&limit=6&recipes_limit=6
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserGetSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes(self, object):
        request = self.context.get("request")
        context = {"request": request}
        recipe_limit = request.query_params.get("recipe_limit")
        queryset = object.recipes.all()
        if recipe_limit:
            queryset = queryset[: int(recipe_limit)]

        return RecipeSubscriptionsSerializer(
            queryset, context=context, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredients")
    author = UserGetSerializer()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        read_only=True, method_name="get_is_favorited"
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True, method_name="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_is_favorited(self, recipe):
        user = self.context["request"].user
        return user.is_authenticated and recipe.favorite.filter(
            user=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context["request"].user
        return user.is_authenticated and recipe.carts.filter(
            user=user).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Subscription
        fields = (
            "author",
            "user",
        )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=["author", "user"],
                message="Вы уже подписаны на этого автора",
            )
        ]

    def create(self, validated_data):
        return Subscription.objects.create(
            user=self.context.get("request").user, **validated_data
        )


class SubscriptionShowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, data):
        recipes_limit = self.context.get(
            "request").query_params.get("recipes_limit")
        recipes = data.author.recipes.all()[: int(recipes_limit)]
        return RecipeSubscriptionsSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name")


class PasswordSetSerializer(UserSerializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "current_password",
            "new_password",
        )

    def validate(self, data):
        user = self.context["request"].user

        if not user.check_password(data["current_password"]):
            raise serializers.ValidationError("Неверный старый пароль.")

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ("user", "recipe")
