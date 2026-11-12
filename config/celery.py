import os

from celery import Celery

# Устанавливаем дефолтный модуль настроек Django для утилиты celery.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("habit_tracker")

# Используем строку конфигурации, которая означает, что сетинги для celery
# будут искаться в settings.py Django с префиксом CELERY_.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находим и загружаем таски из всех зарегистрированных приложений (tasks.py)
app.autodiscover_tasks()
