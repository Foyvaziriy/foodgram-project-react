from typing import Any
import json

from django.core.management.base import BaseCommand, CommandParser
from django.db.utils import IntegrityError

from food.models import Ingredient, MeasurementUnit
from foodgram_backend.settings import BASE_DIR


class Command(BaseCommand):
    help: str = '''Команда для добавления ингредиентов из json файлов.
    Загрузите файл в папку read_json и используйте команду в формате:
    python manage.py add_ingredients <your_file.json>'''
    folder_path: str = BASE_DIR / 'read_json'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('file_name', type=str)

    def handle(self, *args: Any, **options: Any) -> str | None:
        try:
            file = open(
                self.folder_path / options.get('file_name'),
                encoding='utf'
            )
        except FileNotFoundError:
            return 'Файл не найден'

        reader = json.load(file)

        for row in reader:
            try:
                ingredient_name = row['name']
                measurement_unit_name = row['measurement_unit']
            except KeyError:
                self.stdout.write('Ошибка в данных.')
                continue

            measurement_unit, is_created = (
                MeasurementUnit.objects.get_or_create(
                    name=measurement_unit_name
                )
            )
            if is_created:
                self.stdout.write(
                    f'Единица - {measurement_unit} добавлена.')
            else:
                self.stdout.write(
                    f'Единица - {measurement_unit} уже существует.')
            try:
                ingredient, is_created = Ingredient.objects.get_or_create(
                    name=ingredient_name, measurement_unit=measurement_unit
                )
            except IntegrityError as err:
                self.stdout.write(f'Ошибка в данных: {err}')
            if is_created:
                self.stdout.write(f'Ингредиент - {ingredient} добавлен.')
            else:
                self.stdout.write(f'Ингредиент - {ingredient} уже существует.')
