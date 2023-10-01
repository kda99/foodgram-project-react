import csv
import json


from models import Ingredient

def load_data_from_json(file_path):
    with open(file_path) as f:
        data = json.load(f)
        for item in data:
            ingredient = Ingredient(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
            ingredient.save()

# def load_data_from_csv(file_path):
#     with open(file_path) as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             ingredient = Ingredient(name=row['name'], unit=row['unit'])
#             ingredient.save()

# Пример использования для загрузки данных из файлов
load_data_from_json('ingredients.json')
# load_data_from_csv('path/to/ingredients.csv')