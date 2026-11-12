# Habit Tracker Max

Бэкенд-приложение для трекинга полезных привычек на **Django REST Framework**, контейнеризированное с помощью **Docker Compose** и настроенное под **CI/CD** (GitHub Actions).

---

## Архитектура и стек
* **`web`** — Django + DRF + Gunicorn (порт `8000`).
* **`db`** — PostgreSQL 15 (`5432`).
* **`redis`** — брокер для Celery (`6379`).
* **`celery`** / **`celery-beat`** — фоновые задачи и напоминания в MAX.
* **`nginx`** — прокси-сервер (внешний порт **`8082`**).

---

## Локальный запуск

1. **Клонирование репозитория:**
   ```bash
   git clone https://github.com
   cd habit_tracker
   ```
2. **Настройка окружения:** создайте `.env` на основе шаблона и заполните 
   параметры базы данных, Django, Redis и MAX Bot Token.
3. **Запуск через Docker Compose:**
   ```bash
   docker compose up -d --build
   ```
   * **Swagger / Redoc:** `http://localhost:8082/swagger/` | 
     `http://localhost:8082/redoc/`
   * **Админ-панель:** `http://localhost:8082/admin/` *(создать 
     суперпользователя: `docker compose exec web python manage.py createsuperuser`)*.
   * **Остановка:** `docker compose down`.

---

## CI/CD и деплой

Пайплайн (`.github/workflows/ci_cd.yml`) включает этапы: `test` (юнит-тесты), `lint` (flake8), `build` (сборка образов) и `deploy` (автоматический деплой по SSH на сервер при `push`).

1. **Требования к серверу:** установленный Docker / Docker Compose, открытый порт **`8081`**, настроенный SSH-доступ.
2. **GitHub Secrets:** добавьте в настройках репозитория ключи `SERVER_HOST`, `SERVER_USER`, `SSH_PRIVATE_KEY`, а также переменные окружения (`SECRET_KEY`, `ALLOWED_HOSTS`, параметры БД и Telegram).
3. **Продакшен-адреса:**
   * **Админка:** `http://158.160.132.249:8082/admin`