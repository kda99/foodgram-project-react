[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org) [![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org) [![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)](https://nginx.org) [![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com) [![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)](https://www.django-rest-framework.org) [![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)  [![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)](https://github.com) [![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)

# Яндекс.Практикум. Дипломная работа

#### Название: praktikum_new_diplom
#### Папка: foodgram-project-react
#### Группа: когорта 60
#### Когда: 2023 год
#### Кто: Капустин Дмитрий ( https://github.com/kda99/ )

# Описание

Исходный код фронт/бэкенда для онлайн-сервиса «Продуктовый помощник».

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

В данный момент проект запущен на сервере и работает по адресу: http://foodgram.freedynamicdns.net/

# Подготовка и запуск проекта локально

Склонировать репозиторий на локальную машину:
```s
git clone git@github.com:kda99/foodgram-project-react.git
```
Перейти в папку с проектом
```s
cd папка_куда_склонировали/foodgram-project-react
```
Создать виртуальное окружение и обновить pip
```s
python -m venv venv
source venv/Scripts/activate
pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:

```s
pip install -r backend/foodgram_project/requirements.txt
```

Из папки backend/foodgram_project/ выполнить миграции:

```s
python manage.py migrate
```
После этого вы можете работать с api локально обращаясь по адресу: http://127.0.0.1:8000/api/

# Запуск проекта локально в контейнере:

Для этого вам необходимо установить и запустить docket  https://www.docker.com/get-started/

После этого, из консоли, перейти в папку infra и выполнить команду:
```s
docker-compose up -d
```
Запустится рабочий образ сайта по локальным адресам:
- к фронтенду: http://127.0.0.1/
- к документации: http://127.0.0.1/api/docs/redoc.html
- к API: http://127.0.0.1/api/

# Примечания:
В папке /data/ содержатся тестовые данные в формате json для начального наполнения сайта ингредиентами. Загрузка ингредиентов осуществляется посредством  панели администратора, в разделе ингридиенты нажать кнопку Import, выбрать файл ingredients.json, применить импорт.
