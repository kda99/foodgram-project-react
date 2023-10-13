FROM python:3.10-slim

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY .. .

RUN python manage.py collectstatic --no-input

#RUN python manage.py makemigrations

#RUN python manage.py migrate

#RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'a@a.ru', '1')" | python manage.py shell

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000" ]