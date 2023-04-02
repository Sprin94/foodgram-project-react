from django.urls import path, include
from rest_framework.routers import SimpleRouter

from recipes.api.viewsets import TagViewSet, RecipeViewSet, IngredientViewSet

router_v1 = SimpleRouter()

router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router_v1.urls))
]
