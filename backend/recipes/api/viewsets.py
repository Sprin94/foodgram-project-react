from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from recipes.api.serializers import (
    TagSerializer, RecipeSerializer, IngredientSerializer
)
from recipes.models import Tag, Recipe, Ingredient
from core.permission import AuthorOrReadOnly
from recipes.api.filterset import RecipeFilter


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
    # permission_classes = (AuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete',
                         'head', 'options', 'trace')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
