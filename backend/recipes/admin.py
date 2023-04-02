from django.contrib import admin

from recipes.models import Tag, Recipe, Ingredient, RecipeIngredient, Favorite


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('name',),
    }


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredient
    list_display = ('ingredient', 'count',)
    readonly_fields = ('measurement_unit_display',)

    def measurement_unit_display(self, obj):
        return obj.ingredient.measurement_unit
    measurement_unit_display.short_description = 'Единица измерения'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline, ]
    list_filter = (
        'name',
        'author__username',
        'tags',
    )
    readonly_fields = ('get_count_favorites',)

    def get_count_favorites(self, obj):
        return obj.users_favorite.count()
    get_count_favorites.short_description = 'В избранном у'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = (
        'name',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass
