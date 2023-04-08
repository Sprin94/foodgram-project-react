from django.urls import include, path
from recipes.api.viewsets import IngredientViewSet, RecipeViewSet, TagViewSet
from rest_framework.routers import SimpleRouter


router_v1 = SimpleRouter()

router_v1.register("tags", TagViewSet, basename="tags")
router_v1.register("recipes", RecipeViewSet, basename="recipes")
router_v1.register("ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [path("", include(router_v1.urls))]
