import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Import ingredients to DB from json'

    def add_arguments(self, parser):
        parser.add_argument(
            'ingredients',
            default='ingredients.json',
            nargs='?',
            type=str)
        # parser.add_argument(
        #     'tags',
        #     default='tags.json',
        #     nargs='?',
        #     type=str)

    def handle(self, *args, **options):
        try:
            with open('ingredients.json') as f:
                data_tags = json.load(f)
                for tag in data_tags:
                    try:
                        Tag.objects.create(name=tag['name'],
                                           color=tag['color'],
                                           slug=tag['slug'])
                    except IntegrityError:
                        print(f'В базе уже есть: {tag["name"]} ')

            # with open(os.path.join(
            #     settings.MEDIA_ROOT + '/data/', options['ingredients']), 'r',
            #         encoding='utf-8') as f:
            #     data = json.load(f)
            #     for ingredient in data:
            #         try:
            #             Ingredient.objects.create(name=ingredient['name'],
            #                                       measurement_unit=ingredient[
            #                                           'measurement_unit'])
            #         except IntegrityError:
            #             print(f'В базе уже есть: {ingredient["name"]} '
            #                   f'({ingredient["measurement_unit"]})')

        except FileNotFoundError:
            raise CommandError('Файл отсутствует в директории media/data')


# import pandas as pd
# import psycopg2
#
# # Чтение данных из .csv файла
# def load_data():
#     data = pd.read_csv('ingredients.csv')
#
#     # Подключение к базе данных
#     conn = psycopg2.connect(
#         host=DB_HOST,
#         port=DB_PORT,
#         user=POSTGRES_USER,
#         password=POSTGRES_PASSWORD,
#         database=POSTGRES_DB
#     )
#     cursor = conn.cursor()
#
#     # Загрузка данных в базу данных
#     for _, row in data.iterrows():
#         query = f"INSERT INTO ingredients (column1, column2) VALUES ('{row['column1']}', '{row['column2']}')"
#         cursor.execute(query)
#
#     # Сохранение изменений и закрытие соединения
#     conn.commit()
#     cursor.close()
#     conn.close()