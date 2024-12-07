# admin_panel/Dockerfile
FROM python:3.11

# Установка зависимостей
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Копирование проекта
COPY . /app/

# Настройка переменной окружения
ENV DJANGO_SETTINGS_MODULE=myshop.settings

# Открытие порта для Django
EXPOSE 8000

# Команда для запуска Django, обновлена для корректного пути
CMD ["python", "myshop/manage.py", "runserver", "0.0.0.0:8000"]
