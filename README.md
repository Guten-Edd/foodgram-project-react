## Проект: Foodgram - Продуктовый помощник

## Описание
Онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Технологии:

Python 3.7

Django 3.2

Django REST Framework 

PostgreSQL

Docker

nginx

gunicorn


### Подготовка и запуск проекта в Docker

Клонировать репозиторий:

```
git clone git@github.com:Guten-Edd/foodgram-project-react.git
```


Создать infra/.env
Пример заполнения infra/.env:

```
SECRET_KEY=Секретный_ключ
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

Запустить docker-compose:

```
docker-compose up -d
```

Будут созданы и запущены в фоновом режиме необходимые для работы приложения
контейнеры (foodgram-db, foodgram-backend, foodgram-frontend, foodgram-nginx).

Затем нужно внутри контейнера foodgram-backend выполнить миграции, создать 
суперпользователя и собрать статику:

```
docker-compose exec foodgram-backend python manage.py migrate
docker-compose exec foodgram-backend python manage.py createsuperuser
docker-compose exec foodgram-backend python manage.py collectstatic --no-input 
```

После этого проект должен быть доступен по адресу http://localhost/.

### Заполнение базы данных

Нужно зайти на http://localhost/admin/, авторизоваться и внести записи 
в базу данных через админку.

Резервную копию базы данных можно создать командой
```
docker-compose exec foodgram-backend python manage.py dumpdata > fixtures.json 
```

### Остановка контейнеров

Для остановки работы приложения можно набрать в терминале команду Ctrl+C 
либо открыть второй терминал и воспользоваться командой

```
docker-compose stop 
```

Также можно запустить контейнеры без их создания заново командой

```
docker-compose start 
```

Загрузка информации в базу данных:

```
python manage.py csv_import
```

Документация доступна по адресу:

```
http://localhost/api/docs/redoc.html
```

### Автор:
[Эдуард Соловьев](https://github.com/Guten-Edd)

<img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" width="50" height="50"/>