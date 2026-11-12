import os
import random
from datetime import date, datetime

import requests
from celery import shared_task

from habits.models import Habit

VK_BOT_TOKEN = os.getenv("VK_BOT_TOKEN")
VK_ID = os.getenv("VK_ID")


def send_vk_message(user_id, text):
    """Отправка уведомления пользователю через бот ВКонтакте"""
    if not VK_BOT_TOKEN:
        print("Ошибка: не задан VK_BOT_TOKEN в переменных окружения.")
        return

    url = "https://vk.com"
    payload = {
        "user_id": user_id,
        "message": text,
        "random_id": random.randint(1, 2**31 - 1),
        "access_token": VK_BOT_TOKEN,
        "v": "5.199",
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            print(f"Ошибка VK API при отправке пользователю {user_id}: {data['error']['error_msg']}")
    except requests.RequestException as e:
        print(f"Ошибка сети при отправке сообщения в VK пользователю {user_id}: {e}")


@shared_task
def check_and_send_habit_reminders():
    """Периодическая задача проверки привычек и отправки уведомлений в ВК"""
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

        # Проверяем, привязан ли у пользователя VK ID
        if not user.vk_user_id:
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

        # Отправляем уведомление в ВК
        send_vk_message(user.vk_user_id, message)

        # Фиксируем дату отправки
        habit.last_sent = current_date
        habit.save()
