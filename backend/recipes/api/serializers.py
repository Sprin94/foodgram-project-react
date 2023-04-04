from rest_framework.serializers import (
    ModelSerializer, CharField, DecimalField, SerializerMethodField,
    PrimaryKeyRelatedField, Serializer
)
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator

from core.fields import Base64Field
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
        read_only_fields = ('name', 'measurement_unit')


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


class GetRecipeSerializer(ModelSerializer):
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
        queryset = obj.recipeingredient.all()
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


class RecipeIngredientSerializerInline(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = DecimalField(
        max_digits=7,
        decimal_places=2,
        write_only=True,
    )

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class CreateRecipeSerializer(GetRecipeSerializer):
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = UserSerializer(read_only=True)
    image = Base64Field(write_only=True)
    ingredients = RecipeIngredientSerializerInline(many=True)

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        if validated_data.get('ingredients'):
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            for ingredient in ingredients:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount']
                )
        obj = super().update(instance, validated_data)
        return obj


class FavoriteSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже в избранном.'
            )
        ]


class RecipeInlineSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class ShoppingListSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingList
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже в списке покупок.'
            )
        ]
