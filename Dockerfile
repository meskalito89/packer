# Использование минимального базового образа Python
FROM python:3.12-slim AS base

# Создание промежуточного этапа для установки зависимостей
FROM base AS dependencies

# Кэшируем установку зависимостей отдельно от рабочего кода
COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends libxml2-dev libxslt-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# Финальный этап сборки
FROM base AS final

# Копируем только установленные зависимости
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Копируем сам код приложения
COPY . /app
WORKDIR /app

# Удаляем ненужные файлы
RUN find /app -type f -not -name '*.py' -exec rm -f {} +

# Точка входа и дефолтная команда
ENTRYPOINT ["python", "packer.py", "pack"]
CMD ["."]