import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


def amount_validation(value):
    if value <= 0:
        raise ValidationError('Amount must be > 0 ')


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=255,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='slug',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('-id',)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if not re.match('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', self.color):
            raise ValidationError('Invalid HEX color code')


class Recipe(models.Model):
    author = models.ForeignKey(
        verbose_name='Автор',
        to=User,
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
    )
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='recipes/images',
    )
    tags = models.ManyToManyField(
        verbose_name='Тэги',
        to=Tag,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        to='Ingredient',
        through='RecipeIngredient',
        verbose_name="Ингридиенты"
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=100,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=100,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipeingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент',
    )
    amount = models.DecimalField(
        verbose_name='Количество',
        max_digits=7,
        decimal_places=2,
        validators=[amount_validation]
    )

    class Meta:
        verbose_name = 'Ингридиент рецепта'
        verbose_name_plural = 'Ингридиенты рецепта'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient')
        ]

    def __str__(self):
        return self.ingredient.name


class Favorite(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        related_name='favorite_recipes',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        related_name='users_favorite',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe')
        ]

    def __str__(self) -> str:
        return f'{self.user.username} {self.recipe}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        related_name='shopping_list',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        related_name='shopping_list',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoppinglist')
        ]
