#!/bin/sh
# Точка входа backend-контейнера:
#   1) ждём, пока PostgreSQL примет подключения;
#   2) генерируем и применяем миграции;
#   3) запускаем dev-сервер Django.
set -e

echo "==> Ожидание PostgreSQL (${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432})..."
python - <<'PY'
import os
import sys
import time

import psycopg2

for attempt in range(1, 31):
    try:
        psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "coffee"),
            user=os.getenv("POSTGRES_USER", "coffee"),
            password=os.getenv("POSTGRES_PASSWORD", "coffee"),
            host=os.getenv("POSTGRES_HOST", "db"),
            port=os.getenv("POSTGRES_PORT", "5432"),
        ).close()
        print("База данных доступна")
        break
    except psycopg2.OperationalError:
        print(f"  попытка {attempt}/30 — база ещё не готова")
        time.sleep(2)
else:
    sys.exit("Не удалось подключиться к PostgreSQL")
PY

echo "==> Миграции"
# Миграции хранятся в репозитории. makemigrations вызываем на случай, если модели
# изменили после последней сборки: новая миграция создастся автоматически.
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "==> Запуск Django на 0.0.0.0:8000"
exec python manage.py runserver 0.0.0.0:8000
