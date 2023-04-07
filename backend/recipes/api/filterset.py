from django_filters import CharFilter, FilterSet, NumberFilter
from recipes.models import Ingredient, Recipe


class RecipeFilter(FilterSet):
    is_favorited = NumberFilter(
        method="filter_is_favorited",
        label="is_favorited",
    )
    is_in_shopping_cart = NumberFilter(
        method="filter_is_in_shopping_cart",
        label="is_in_shopping_cart",
    )
    author = CharFilter(field_name="author")
    tags = CharFilter(field_name="tags__slug")

    class Meta:
        model = Recipe
        fields = ["is_favorited", "is_in_shopping_cart", "author", "tags"]

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            favorited_recipe = user.favorite_recipes.values_list(
                "recipe_id",
                flat=True,
            )
            return queryset.filter(id__in=favorited_recipe)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            favorited_recipe = user.shopping_list.values_list(
                "recipe_id",
                flat=True,
            )
            return queryset.filter(id__in=favorited_recipe)
        return queryset


class IngredientFilter(FilterSet):
    name = CharFilter(method="filter_name")

    class Meta:
        model = Ingredient
        fields = ("name",)

    def filter_name(self, queryset, name, value):
        if value:
            return queryset.filter(name__startswith=value)
        return queryset
