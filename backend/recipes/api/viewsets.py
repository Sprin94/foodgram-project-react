from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.api.serializers import (
    TagSerializer, RecipeSerializer, IngredientSerializer
)
from recipes.models import Tag, Recipe, Ingredient


class TagViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
