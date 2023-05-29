import csv

from app.models import Ingredient
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Запуск произвести командой python manage.py csv_import
    Заполнить базу можно только один раз, при повторном заполнении
    появится ошибка.
    """
    def handle(self, *args, **kwargs):
        model = Ingredient
        csv_f = 'ingredients.csv'
        with open(
            f'{settings.BASE_DIR}/static/data/{csv_f}',
            newline='',
            encoding='utf-8'
        ) as csv_file:
            reader = csv.reader(csv_file)
            count = 0
            for row in reader:
                name, unit = row
                model.objects.get_or_create(name=name,
                                            measurement_unit=unit)
                count += 1
                if not count % 100:
                    print(f'Обработано: {count} записей.')

        self.stdout.write(self.style.SUCCESS('Данные загружены'))
