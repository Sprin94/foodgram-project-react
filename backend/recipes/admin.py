from django.contrib import admin
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ модель Tag."""

    prepopulated_fields = {
        "slug": ("name",),
    }


class RecipeIngredientInline(admin.StackedInline):
    """Инлайн модель RecipeIngredient."""

    model = RecipeIngredient
    list_display = (
        "ingredient",
        "amount",
    )
    readonly_fields = ("measurement_unit_display",)

    def measurement_unit_display(self, obj):
        return obj.ingredient.measurement_unit

    measurement_unit_display.short_description = "Единица измерения"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ модель Recipe."""

    inlines = [
        RecipeIngredientInline,
    ]
    list_filter = (
        "name",
        "author__username",
        "tags",
    )
    list_display = (
        "name",
        "author",
    )
    search_fields = (
        "author__username",
        "name",
    )
    readonly_fields = ("get_count_favorites",)

    def get_count_favorites(self, obj):
        return obj.users_favorite.count()

    get_count_favorites.short_description = "В избранном у"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ модель Ingredient."""

    list_filter = ("name",)
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = (
        "name",
        "measurement_unit",
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ модель Favorite."""


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Админ модель ShoppingList."""
