from rest_framework.serializers import (
    ModelSerializer, CharField, DecimalField, SerializerMethodField
)
from django.contrib.auth import get_user_model

from recipes.models import (Tag, Recipe, RecipeIngredient, Favorite,
                            Ingredient, ShoppingList)

from users.api.serializers import UserSerializer


User = get_user_model()


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class RecipeIngredientSerializer(ModelSerializer):
    name = CharField(
        read_only=True,
        source='ingredient.name',
    )
    measurement_unit = CharField(
        read_only=True,
        source='ingredient.measurement_unit',
    )
    amount = DecimalField(
        max_digits=7,
        decimal_places=2,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, obj):
        queryset = obj.count_ingredients.all()
        serializer = RecipeIngredientSerializer(queryset, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingList.objects.filter(user=user, recipe=obj).exists()
        return False
