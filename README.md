# ☕ Coffee Shop — учебный интернет-магазин кофе

Веб-приложение с разделённым frontend (Vue 3 + Vite) и backend (Django + DRF),
PostgreSQL и Docker. Проект сделан максимально просто, но закрывает все
требования учебного задания: роли, JWT, каталог с фильтрами, заказы, отзывы
и выгрузку отчётов в XLSX.

## Стек

| Слой | Технологии |
|---|---|
| Backend | Django 5, Django REST Framework, SimpleJWT, openpyxl, Pillow |
| БД | PostgreSQL 16 |
| Frontend | Vue 3 (Composition API), Vue Router, Pinia, Axios, Vite |
| Инфраструктура | Docker Compose (db / backend / frontend) |

## Быстрый старт

```bash
# 1. Переменные окружения
cp .env.example .env          # Windows (cmd): copy .env.example .env

# 2. Сборка и запуск всех сервисов
docker compose up --build
```

После старта:

| Что | URL |
|---|---|
| Frontend (каталог) | http://localhost:5173 |
| Backend API | http://localhost:8000/api/ |
| Django admin | http://localhost:8000/admin/ |
| Страница отчётов (в SPA) | http://localhost:5173/admin/reports |

### Суперпользователь (администратор)

```bash
docker compose exec backend python manage.py createsuperuser
```

Логин/пароль, созданный этой командой, работает и в Django admin, и в SPA:
у суперпользователя роль автоматически становится `admin` (см. `User.save()`).

### Демо-данные (необязательно)

```bash
docker compose exec backend python manage.py seed_demo
```

Команда создаёт 3 категории и 7 товаров, чтобы каталог был не пустым.

## Структура проекта

```
.
├── backend/
│   ├── config/            # настройки Django, urls, BaseModel
│   ├── users/             # кастомный User, JWT-аутентификация, permissions
│   ├── shop/              # Category, Product, Order, OrderItem, Review
│   ├── reports/           # выгрузка XLSX (openpyxl)
│   ├── templates/admin/   # минимальная стилизация Django admin
│   ├── manage.py
│   ├── requirements.txt
│   ├── entrypoint.sh      # ожидание БД → makemigrations/migrate → runserver
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/         # страницы SPA
│   │   ├── components/    # NavBar, ProductCard
│   │   ├── router/        # маршруты + guards по ролям
│   │   ├── store/         # Pinia: auth, cart
│   │   ├── api/           # axios + интерцептор Authorization
│   │   └── utils/         # форматирование цены/дат, разбор ошибок
│   ├── package.json
│   ├── vite.config.js     # прокси /api и /media → backend:8000
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
└── .gitignore
```

> **Про миграции.** Файлы миграций лежат в `backend/*/migrations/`.
> `entrypoint.sh` при старте дополнительно выполняет `makemigrations` + `migrate`:
> если модели изменились, новая миграция создастся автоматически, а если нет —
> команда просто ничего не сделает.

## Роли и доступ

| Роль | Возможности |
|---|---|
| Гость | каталог, карточка товара, опубликованные отзывы |
| Пользователь | всё выше + оформление заказа, свои заказы, отзывы |
| Администратор | всё выше (видит все заказы) + Django admin + `/admin/reports` |

Разграничение сделано на двух уровнях:

* **Backend** — DRF permissions: `IsAuthenticated`, кастомные
  `IsAdminRole` и `IsOwnerOrAdmin` (`backend/users/permissions.py`).
* **Frontend** — `meta.requiresAuth` / `meta.requiresAdmin` в
  `frontend/src/router/index.js` (это только UX, сервер проверяет права сам).

## API (кратко)

| Метод | URL | Доступ |
|---|---|---|
| POST | `/api/auth/register/` | все |
| POST | `/api/auth/login/` | все |
| POST | `/api/auth/refresh/` | все |
| GET | `/api/auth/me/` | авторизованные |
| GET | `/api/categories/` | все |
| GET | `/api/products/?category=<slug>&ordering=price&search=<text>` | все |
| GET | `/api/products/<id>/` | все |
| GET | `/api/products/<id>/reviews/` | все (только опубликованные) |
| POST | `/api/products/<id>/reviews/` | авторизованные |
| GET | `/api/orders/` | авторизованные (свои; админ — все) |
| POST | `/api/orders/` | авторизованные |
| GET | `/api/orders/<id>/` | владелец или админ |
| GET | `/api/reports/schema/` | админ |
| POST | `/api/reports/export/` | админ |

JWT передаётся в заголовке `Authorization: Bearer <access>`.
Токен хранится в `localStorage`, axios-интерцептор подставляет его автоматически
(`frontend/src/api/index.js`).

### Пример оформления заказа

```json
POST /api/orders/
{
  "address": "г. Москва, ул. Тверская, д. 1",
  "items": [
    { "product": 1, "quantity": 2 },
    { "product": 5, "quantity": 1 }
  ]
}
```

Сумма и цены считаются на сервере по актуальному прайсу, остатки товаров
уменьшаются в транзакции (`select_for_update`).

### Пример выгрузки отчёта

```json
POST /api/reports/export/
{
  "tables": {
    "products": ["id", "name", "price"],
    "orders": ["id", "status", "total_price"]
  }
}
```

Ответ — файл `.xlsx`, где каждая выбранная таблица лежит на отдельном листе.
Список доступных таблиц и полей отдаёт `GET /api/reports/schema/`, страница
`/admin/reports` строит по нему чекбоксы.

## Безопасность (что и почему)

* **SQL-инъекции** — только ORM, без `raw()`/`extra()`. Имена полей отчёта
  проверяются по белому списку `TABLES` в `backend/reports/views.py`.
* **XSS** — Vue экранирует вывод по умолчанию, `v-html` нигде не используется.
  На бэкенде входные данные валидируются сериализаторами DRF.
* **Пароли** — стандартный хэш Django (`create_user` → `set_password`).
* **Права** — проверяются на сервере, фронтенд-проверки лишь для удобства.
* **CORS** — `django-cors-headers`, список origin'ов в `.env` (`CORS_ORIGINS`).

## Адаптивность

Три контрольные точки, как в задании:

* мобильный — `≤ 576px`;
* планшет — `577–992px`;
* десктоп — `≥ 993px`.

Реализовано на CSS Grid/Flex + media queries в `frontend/src/style.css`,
без UI-библиотек.

## Полезные команды

```bash
docker compose up --build        # запуск/пересборка
docker compose down              # остановка
docker compose down -v           # остановка + удаление БД и медиа
docker compose logs -f backend   # логи Django
docker compose exec backend python manage.py shell
docker compose exec backend python manage.py createsuperuser
```

## Возможные проблемы

* **`docker compose` не находит `.env`** — скопируйте `.env.example` в `.env`.
* **Порт занят** — освободите 5173/8000 или измените проброс портов в
  `docker-compose.yml`.
* **Фронтенд не видит API** — проверьте, что `VITE_API_TARGET` в compose
  указывает на `http://backend:8000` (внутри сети Docker).
* **Картинки товаров 404** — в dev их отдаёт Django (`DEBUG=1`), файлы лежат
  в volume `media_data`; загрузка — через Django admin.
