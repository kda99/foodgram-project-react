import json
import os

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Import ingredients to DB from json'

    def run():
        ingredients_file = 'ingredients.json'

        try:
            with open(ingredients_file) as f:
                data = json.load(f)
                for ingredient in data:
                    try:
                        Ingredient.objects.create(name=ingredient['name'],
                                                  measurement_unit=ingredient['measurement_unit'])
                    except IntegrityError:
                        print(f'В базе уже есть: {ingredient["name"]} ({ingredient["measurement_unit"]})')

        except FileNotFoundError:
            print('Файл отсутствует в директории media/data')
