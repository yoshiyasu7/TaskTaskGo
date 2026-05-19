# ✅ TaskTaskGo

> Веб-приложение для управления проектами и задачами с REST API, фоновой обработкой результатов и уведомлениями в реальном времени.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.118+-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)

---

## 📋 Содержание

- [О проекте](#-о-проекте)
- [Быстрый старт](#-быстрый-старт)
- [Архитектура](#-архитектура)
- [Структура проекта](#-структура-проекта)
- [API эндпоинты](#-api-эндпоинты)
- [Таблицы базы данных](#-таблицы-базы-данных)
- [Конфигурация](#-конфигурация)
- [Качество и тестирование](#-качество-и-тестирование)

---

## 🎯 О проекте

**TaskTaskGo** - backend-сервис и веб-интерфейс для работы с проектами и задачами. Пользователь создаёт проекты, добавляет в них задачи, а после создания задачи система в фоне генерирует JSON-результат, сохраняет его в S3-хранилище и уведомляет пользователя через Socket.IO.

### Основные возможности

| Функция | Описание |
|---------|----------|
| 🔐 **Аутентификация** | Регистрация, вход, выход и получение профиля по JWT |
| 📁 **Проекты** | CRUD для проектов, привязанных к пользователю |
| 📝 **Задачи** | CRUD для задач внутри проектов со статусами |
| ⚙️ **Фоновая обработка** | Генерация JSON через внешний API и загрузка результата в S3 |
| 🔔 **Уведомления** | Real-time оповещения о завершении задачи через Socket.IO |
| 🌐 **Веб-интерфейс** | HTML-страницы на Jinja2 для регистрации, профиля и управления сущностями |
| 📱 **Мониторинг ошибок** | Отправка необработанных исключений в Telegram |

### Ключевые особенности

- ⚡ **Асинхронный стек**: FastAPI + SQLAlchemy Async + asyncpg.
- 🧩 **Слоистая архитектура**: разделение на domain, application, infrastructure и API-слой.
- 🛡️ **Безопасность**: JWT-аутентификация и хеширование паролей (bcrypt).
- ☁️ **Интеграции**: JSONBin.io для генерации JSON, Yandex Object Storage (S3) для хранения результатов.
- 🔄 **Миграции**: Alembic для версионирования схемы PostgreSQL.

---

## 🚀 Быстрый старт

### Требования

- Python 3.10+
- Poetry
- PostgreSQL 17+ (для локального запуска без Docker)
- Docker + Docker Compose (для контейнерного запуска)

### Локальный запуск

```bash
# 1. Установка зависимостей
poetry install

# 2. Создание env
cp settings/.env.example settings/.env
# Заполните обязательные переменные (SECRET_KEY, ALGORITHM, DB_* и др.)

# 3. Миграции
alembic upgrade head

# 4. Запуск приложения
make run
```

**API:** `http://127.0.0.1:8000`  
**Swagger UI:** `http://127.0.0.1:8000/docs`

### Запуск в Docker Compose

```bash
# 1. Подготовка env
cp settings/.env.example settings/.env
# Заполните обязательные переменные

# 2. Запуск сервисов
docker compose -f settings/docker-compose.yaml up --build -d
```

Приложение будет доступно на порту, указанном в `APP_PORT_OUTSIDE` (по умолчанию `8080`).

---

## 🏗 Архитектура

Проект организован по слоям: бизнес-модели и правила отделены от инфраструктуры и HTTP-слоя.

### Слои

| Слой | Путь | Ответственность |
|------|------|-----------------|
| **Domain** | `src/domain/` | SQLAlchemy-модели сущностей и перечисления |
| **Application** | `src/application/` | Бизнес-методы и сервисы (обработка задач) |
| **Infrastructure** | `src/infrastructure/` | DAO, подключение к БД, S3-клиент |
| **API** | `src/api/` | FastAPI-роутеры, схемы Pydantic, конфигурация, безопасность, Socket.IO |
| **Utils** | `src/utils/` | Логирование, интеграции с внешними API, Telegram |

### Поток обработки задачи

```text
HTTP POST /api/v1/tasks/
  -> Router (FastAPI)
  -> Application method (add_task)
  -> DAO / PostgreSQL
  -> BackgroundTasks
  -> TaskProcessingService
      -> JSONBin API (генерация JSON)
      -> S3 (сохранение результата)
      -> Обновление tasks.result_url
      -> Socket.IO (уведомление пользователя)
```

---

## 📁 Структура проекта

```text
TaskTaskGo/
├── pyproject.toml                 # Зависимости (Poetry)
├── Makefile                       # Команды запуска, Docker и проверок
├── Dockerfile                     # Multi-stage образ приложения
├── alembic.ini                    # Конфигурация Alembic
├── migration/                     # Миграции БД
├── settings/
│   ├── .env.example               # Переменные окружения
│   ├── docker-compose.yaml        # Контейнеры app + postgres
│   └── settings.json              # Настройки логирования
├── src/
│   ├── api/                       # FastAPI, роутеры, схемы, security, Socket.IO
│   ├── application/               # Методы и сервисы бизнес-логики
│   ├── domain/                    # Модели User, Project, Task
│   ├── infrastructure/            # DAO, database, S3
│   ├── utils/                     # Логирование, JSON-сервис, Telegram
│   └── main.py                    # Точка входа приложения
├── static/                        # CSS и JavaScript для веб-интерфейса
└── templates/                     # Jinja2 HTML-шаблоны
```

---

## 🔌 API эндпоинты

Базовый префикс API: `/api/v1`

### Authentication

| Метод | Эндпоинт | Описание | Доступ |
|------|----------|----------|--------|
| POST | `/api/v1/auth/register/` | Регистрация пользователя | Public |
| POST | `/api/v1/auth/login/` | Вход и выдача JWT-токена | Public |
| GET | `/api/v1/auth/user/` | Информация о текущем пользователе | Auth |
| POST | `/api/v1/auth/logout/` | Выход из аккаунта | Auth |

### Projects

| Метод | Эндпоинт | Описание | Доступ |
|------|----------|----------|--------|
| POST | `/api/v1/projects/` | Создание проекта | Auth |
| GET | `/api/v1/projects/` | Список проектов пользователя | Auth |
| PUT | `/api/v1/projects/{project_id}` | Обновление проекта | Auth |
| POST | `/api/v1/projects/{project_id}` | Удаление проекта | Auth |

### Tasks

| Метод | Эндпоинт | Описание | Доступ |
|------|----------|----------|--------|
| POST | `/api/v1/tasks/` | Создание задачи (с фоновой обработкой) | Auth |
| GET | `/api/v1/tasks/` | Список задач (фильтр по `project_id`) | Auth |
| PUT | `/api/v1/tasks/{task_id}` | Обновление задачи | Auth |
| POST | `/api/v1/tasks/{task_id}` | Удаление задачи | Auth |

### Web-страницы

| Метод | Эндпоинт | Описание |
|------|----------|----------|
| GET | `/register` | Страница регистрации |
| GET | `/login` | Страница входа |
| GET | `/profile` | Профиль пользователя |
| GET | `/logout` | Страница выхода |
| GET | `/notifications` | Страница Socket.IO-уведомлений |
| GET | `/projects/create` | Создание проекта |
| GET | `/projects/{project_id}/edit` | Редактирование проекта |
| GET | `/projects/{project_id}/delete` | Удаление проекта |
| GET | `/tasks/create` | Создание задачи |
| GET | `/tasks/{task_id}/edit` | Редактирование задачи |
| GET | `/tasks/{task_id}/delete` | Удаление задачи |

---

## 🗃 Таблицы базы данных

Ниже перечислены таблицы, которые формируются миграциями Alembic и SQLAlchemy-моделями.

| Таблица | Назначение | Ключевые поля | Связи |
|---------|------------|---------------|-------|
| `users` | Учётные записи пользователей | `id`, `username`, `password`, `created_at`, `updated_at` | `1:N` с `projects`, `1:N` с `tasks` |
| `projects` | Проекты пользователя | `id`, `title`, `content`, `user_id`, `created_at`, `updated_at` | `N:1` к `users`, `1:N` с `tasks` |
| `tasks` | Задачи внутри проектов | `id`, `title`, `content`, `status`, `user_id`, `project_id`, `result_url`, `created_at`, `updated_at` | `N:1` к `users`, `N:1` к `projects` |

### Детализация полей

#### `users`

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | `INTEGER` | PK, autoincrement | Идентификатор пользователя |
| `username` | `VARCHAR` | NOT NULL, UNIQUE | Логин пользователя |
| `password` | `VARCHAR` | NOT NULL | Хеш пароля (bcrypt) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | Дата создания записи |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | Дата последнего обновления |

#### `projects`

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | `INTEGER` | PK, autoincrement | Идентификатор проекта |
| `title` | `VARCHAR` | NOT NULL, UNIQUE | Название проекта |
| `content` | `VARCHAR` | NOT NULL | Описание проекта |
| `user_id` | `INTEGER` | NOT NULL, FK → `users.id` | Владелец проекта |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | Дата создания записи |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | Дата последнего обновления |

#### `tasks`

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | `INTEGER` | PK, autoincrement | Идентификатор задачи |
| `title` | `VARCHAR` | NOT NULL | Название задачи |
| `content` | `VARCHAR` | NOT NULL | Содержание задачи |
| `status` | `statustask` (ENUM) | NOT NULL, default `IN_PROGRESS` | Статус задачи |
| `user_id` | `INTEGER` | NOT NULL, FK → `users.id` | Автор задачи |
| `project_id` | `INTEGER` | NOT NULL, FK → `projects.id` ON DELETE CASCADE | Проект задачи |
| `result_url` | `VARCHAR` | NULL | URL результата обработки в S3 |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | Дата создания записи |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | Дата последнего обновления |

### Значения ENUM `statustask`

| Значение | Отображение |
|----------|-------------|
| `IN_PROGRESS` | В работе |
| `DELETED` | Удалена |
| `SUSPENDED` | Отложена |

### ER-схема связей

```text
users (1) ──< projects (N)
users (1) ──< tasks (N)
projects (1) ──< tasks (N)   [ON DELETE CASCADE]
```

### Важные ограничения

- `users.username` - уникальный логин.
- `projects.title` - уникальное название проекта.
- `tasks.project_id` - каскадное удаление задач при удалении проекта.
- Все таблицы наследуют базовые поля `id`, `created_at`, `updated_at` из абстрактной модели `Base`.

---

## ⚙️ Конфигурация

Основной файл окружения: `settings/.env.example` → `settings/.env`.

| Группа | Примеры | Назначение |
|--------|---------|------------|
| App | `APP_HOST`, `APP_PORT`, `APP_PORT_OUTSIDE` | Параметры FastAPI/Uvicorn |
| DB | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Подключение к PostgreSQL |
| JWT | `SECRET_KEY`, `ALGORITHM` | Аутентификация и подпись токенов |
| JSONBin | `X_MASTER_KEY`, `X_ACCESS_KEY` | Генерация JSON для задач |
| S3 | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_BUCKET`, `AWS_ENDPOINT_URL` | Хранение результатов |
| Telegram | `TG_BOT_TOKEN`, `TG_CHAT_ID` | Уведомления об ошибках |
| Logging | `settings/settings.json` | Уровень логов, формат, ротация |

---

## 🧪 Качество и тестирование

```bash
# Unit-тесты
make test

# Форматирование и статический анализ
make check
```

Используется:

- `pytest`
- `black`, `isort`
- `flake8`, `ruff`, `mypy`, `pylint`
