from django.contrib.auth import get_user_model
from django.db.models import Sum, F

from recipes.models import ShoppingList

User = get_user_model()


def get_shopping_list(user: User):
    shop_list = (
        ShoppingList.objects
        .filter(user=user.id)
        .prefetch_related('recipe')
        .values(name=F('recipe__ingredients__name'),
                unit=F(
                    'recipe__recipeingredient__ingredient__measurement_unit'))
        .annotate(total_amount=Sum('recipe__recipeingredient__amount'))
        .order_by('recipe__ingredients__name')
    )

    return '\n'.join(
        f'{i["name"]}({i["unit"]}) - {i["total_amount"]}' for i in shop_list
    )
