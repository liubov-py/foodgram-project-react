import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Заполнение БД данными из csv-файлов'

    def handle(self, *args, **kwargs):
        self.stdout.write('Импорт ингредиентов')
        Ingredient.objects.all().delete()
        print(os.getcwd())
        with open('data/ingredients.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                category = Ingredient(name=row['name'],
                                      measurement_unit=row['measurement_unit'])
                category.save()
                line_count += 1
        self.stdout.write('Добавлено строк %s' % line_count)
