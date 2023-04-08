import csv
import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("Importing data from: %s", settings.BASE_DIR)

        with open(
            os.path.join(settings.BASE_DIR, "ingredients.csv"),
            "r",
            encoding="UTF-8",
        ) as ingredients:
            ingredients_file = csv.reader(ingredients)
            for counter, line in enumerate(ingredients_file):
                name = line[0]
                measurement_unit = line[1]
                obj, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit,
                )

                if not created:
                    print(name)
                    obj.name = name
                    obj.measurement_unit = measurement_unit
                    obj.save()
                print(counter, created)
        print("Finish")
