import os
import requests
from datetime import datetime, date
from celery import shared_task
from habits.models import Habit

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Прокси берется из .env
PROXY_URL = os.getenv("TELEGRAM_PROXY", None)


def send_telegram_message(chat_id, text):
    """Отправка сообщения в Telegram-бот с поддержкой прокси для обхода блокировок"""
    if not TELEGRAM_BOT_TOKEN:
        print("Ошибка: не задан TELEGRAM_BOT_TOKEN в переменных окружения.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    # Настройка прокси при наличии в .env
    proxies = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None

    try:
        response = requests.post(url, json=payload, proxies=proxies, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка отправки сообщения в Telegram чат {chat_id}: {e}")


@shared_task
def check_and_send_habit_reminders():
    """Периодическая задача проверки привычек и отправки уведомлений"""
    current_time = datetime.now().time()
    current_date = date.today()

    # Фильтруем полезные привычки (is_pleasant=False), у которых совпадает час и минута
    habits = Habit.objects.filter(
        time__hour=current_time.hour,
        time__minute=current_time.minute,
        is_pleasant=False,
    )

    for habit in habits:
        user = habit.user

        # Проверяем, привязан ли у пользователя Telegram Chat ID
        if not user.tg_chat_id:
            continue

        # Проверяем периодичность выполнения
        if habit.last_sent:
            days_passed = (current_date - habit.last_sent).days
            if days_passed < habit.periodicity:
                continue

        # Формируем текст сообщения
        message = (
            f"⏰ Напоминание о привычке!\n"
            f"Действие: {habit.action}\n"
            f"Место: {habit.place}\n"
            f"Время: {habit.time.strftime('%H:%M')}\n"
        )

        if habit.reward:
            message += f"🎁 Вознаграждение: {habit.reward}"
        elif habit.associated_habit:
            message += f"🎉 Приятная привычка после: {habit.associated_habit.action}"

        # Отправляем уведомление
        send_telegram_message(user.tg_chat_id, message)

        # Фиксируем дату отправки
        habit.last_sent = current_date
        habit.save()
