FROM python:3.10-slim

# Установим системные зависимости и PostgreSQL-клиент
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем Python-библиотеки
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Указываем команду для запуска бота
CMD ["python", "main.py"]
