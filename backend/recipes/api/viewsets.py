from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, filters
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated

from recipes.api.serializers import (
    TagSerializer, GetRecipeSerializer, IngredientSerializer,
    FavoriteSerializer, RecipeInlineSerializer, ShoppingListSerializer,
    CreateRecipeSerializer
)
from recipes.models import Tag, Recipe, Ingredient, Favorite, ShoppingList
from core.permission import AuthorOrReadOnly
from recipes.api.filterset import RecipeFilter
from recipes.api.services import get_shopping_list

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete',
                         'head', 'options', 'trace')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        context = {'request': request}
        serializer = CreateRecipeSerializer(recipe,
                                            data=request.data,
                                            context=context,
                                            partial=True,
                                            )
        if serializer.is_valid():
            obj = serializer.save()
            return Response(GetRecipeSerializer(obj, context=context).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        context = {'request': request}
        serializer = CreateRecipeSerializer(data=request.data,
                                            context=context,
                                            )
        if serializer.is_valid():
            obj = serializer.save()
            return Response(GetRecipeSerializer(obj, context=context).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return CreateRecipeSerializer

    @action(detail=True, methods=('POST', 'DELETE'), url_path='favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        data = {'user': request.user.id,
                'recipe': pk}

        if request.method == 'POST':
            serializer = FavoriteSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                recipe = Recipe.objects.get(pk=pk)
                return Response(RecipeInlineSerializer(recipe).data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        favorite = Favorite.objects.filter(**data)
        if favorite:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Вы не добавили рецепт в избранное'})

    @action(detail=True, methods=('POST', 'DELETE'), url_path='shopping_cart',
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        data = {'user': request.user.id,
                'recipe': pk}
        if request.method == 'POST':
            serializer = ShoppingListSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                recipe = Recipe.objects.get(pk=pk)
                return Response(RecipeInlineSerializer(recipe).data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        recipe_list = ShoppingList.objects.filter(**data)
        if recipe_list:
            recipe_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Вы не добавляли рецепт в список покупок'})

    @action(detail=False, methods=('GET',), url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        list = get_shopping_list(user=request.user)
        response = HttpResponse(list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="list.txt"'
        return response
