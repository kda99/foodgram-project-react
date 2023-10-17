import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Import ingredients to DB from json'

    def run():
        ingredients_file = 'ingredients.json'
        # tags_file = 'tags.json'

        try:
            with open(os.path.join(settings.MEDIA_ROOT, 'data', ingredients_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                for ingredient in data:
                    try:
                        Ingredient.objects.create(name=ingredient['name'],
                                                  measurement_unit=ingredient['measurement_unit'])
                    except IntegrityError:
                        print(f'В базе уже есть: {ingredient["name"]} ({ingredient["measurement_unit"]})')

            # with open(os.path.join(settings.MEDIA_ROOT, 'data', tags_file), 'r', encoding='utf-8') as f:
            #     data_tags = json.load(f)
            #     for tag in data_tags:
            #         try:
            #             Tag.objects.create(name=tag['name'], color=tag['color'], slug=tag['slug'])
            #         except IntegrityError:
            #             print(f'В базе уже есть: {tag["name"]}')

        except FileNotFoundError:
            print('Файл отсутствует в директории media/data')
