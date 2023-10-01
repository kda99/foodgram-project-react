import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers



from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient, Cart
from users.models import User, Subscription


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class TagIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id',)



class IngredientSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(source='ingredient.id')
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')



class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients', read_only=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',)

    def create(self, validated_data):
        ingredients = self.initial_data.get('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(
            **validated_data
        )
        for ingredient in ingredients:
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            ).save()
        recipe.tags.set(tags)
        return recipe



class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False

        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class RecipeSubscriptionsSerializer(serializers.ModelSerializer):


    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserSubscripterSeralizer(serializers.ModelSerializer):
    """
    /api/users/subscriptions/?page=1&limit=6&recipes_limit=6
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserGetSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )


    def get_recipes(self, object):
        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipe_limit')
        queryset = object.recipes.all()
        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]

        return RecipeSubscriptionsSerializer(queryset, context=context, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')
    author = UserGetSerializer()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Subscription
        fields = ('author', 'user', )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['author', 'user'],
                message="Вы уже подписаны на этого автора"
            )
        ]

    def create(self, validated_data):
        return Subscription.objects.create(
            user=self.context.get('request').user, **validated_data)




class SubscriptionShowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')


    def get_recipes(self, data):
        recipes_limit = self.context.get('request').query_params.get('recipes_limit')
        recipes = data.author.recipes.all()[:int(recipes_limit)]
        return RecipeSubscriptionsSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class PasswordSetSerializer(UserSerializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


    class Meta:
        model = User
        fields = ('current_password', 'new_password',)

    def validate(self, data):
        user = self.context['request'].user

        if not user.check_password(data['current_password']):
            raise serializers.ValidationError("Неверный старый пароль.")

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

class CartSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    is_in_shopping_cart = serializers.BooleanField(source='recipe.is_in_shopping_cart')
    class Meta:
        model = Cart
        fields = ('name', 'image', 'cooking_time', 'is_in_shopping_cart')