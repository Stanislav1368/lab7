# Backend: Django + DRF + PostgreSQL (учебный проект, dev-режим).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Сначала ставим зависимости — слой кэшируется, пока не изменился requirements.txt.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# entrypoint.sh: ждём PostgreSQL, генерируем/применяем миграции, запускаем runserver.
ENTRYPOINT ["sh", "entrypoint.sh"]
