# Базовый образ с Python
FROM python:3.12-slim

# Установка зависимостей
COPY requirements.txt .
RUN apt update && apt install -y git
RUN pip install --no-cache-dir -r requirements.txt

# Добавляем рабочий код
COPY . /app
WORKDIR /app

# Запускаем команду packer
ENTRYPOINT ["python", "packer.py", "pack"] 
CMD ['.']