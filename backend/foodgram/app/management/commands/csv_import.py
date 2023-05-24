import csv

from django.conf import settings
from django.core.management import BaseCommand
from app.models import Ingredient



class Command(BaseCommand):
    """
    Запуск произвести командой python manage.py csv_import
    Заполнить базу можно только один раз, при повторном заполнении
    появится ошибка.
    Для удаления БД можно просто удалить файл db.sqlite3
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
                    model.objects.get_or_create(name=name, measurement_unit=unit)
                    count += 1
                    if not count % 100:
                        print(f'Обработано: {count} записей.')

        self.stdout.write(self.style.SUCCESS('Данные загружены'))
