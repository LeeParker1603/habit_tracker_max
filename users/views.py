import json
import os
import random

import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from users.models import User
from users.serializers import UserRegisterSerializer


class UserRegisterView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


@csrf_exempt
def vk_callback(request):
    # ВК всегда присылает события методом POST
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    # Читаем JSON из тела запроса
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON", status=400)

    # Проверяем секретный ключ
    secret_key = os.getenv("VK_SECRET_KEY")
    if secret_key and data.get("secret") != secret_key:
        return HttpResponse("Forbidden", status=403)

    # 1. Главный шаг для подтверждения сервера
    if data.get("type") == "confirmation":
        confirmation_code = os.getenv("VK_CONFIRMATION_CODE", "")
        return HttpResponse(confirmation_code, content_type="text/plain")

        # 2. Обработка входящего сообщения и привязки аккаунта
    if data.get("type") == "message_new":
        message = data.get("object", {}).get("message", {})
        vk_user_id = str(message.get("from_id", ""))
        text = message.get("text", "").strip()

        # Пробуем взять email из метки ?ref= или из текста сообщения (если пользователь прислал свой email)
        ref_email = message.get("ref") or (text if "@" in text else None)

        vk_token = os.getenv("VK_BOT_TOKEN")

        if ref_email and vk_user_id:
            user = User.objects.filter(email__iexact=ref_email).first()
            if user:
                user.vk_user_id = vk_user_id
                user.save()

                if vk_token:
                    requests.post(
                        "https://api.vk.ru/method/messages.send",
                        data={
                            "user_id": vk_user_id,
                            "message": f"Аккаунт {user.email} успешно привязан! Тестовое уведомление работает.",
                            "random_id": random.randint(1, 2**31),
                            "access_token": vk_token,
                            "v": "5.199",
                        },
                        timeout=5,
                    )
            elif vk_token:
                # Если email не найден в базе — подсказываем пользователю
                requests.post(
                    "https://api.vk.ru/method/messages.send",
                    data={
                        "user_id": vk_user_id,
                        "message": f"Пользователь с email {ref_email} не найден на сайте. Проверьте адрес и отправьте его снова.",
                        "random_id": random.randint(1, 2**31),
                        "access_token": vk_token,
                        "v": "5.199",
                    },
                    timeout=5,
                )
        elif vk_user_id and vk_token:
            # Если пришло обычное сообщение без ref (например, повторное "Начать")
            requests.post(
                "https://api.vk.ru/method/messages.send",
                data={
                    "user_id": vk_user_id,
                    "message": "Привет! Чтобы привязать аккаунт, перейдите по кнопке из личного кабинета на сайте или просто отправьте сюда свой email, указанный при регистрации.",
                    "random_id": random.randint(1, 2**31),
                    "access_token": vk_token,
                    "v": "5.199",
                },
                timeout=5,
            )

    # 3. Для всех остальных событий пока просто отвечаем "ok"
    return HttpResponse("ok", content_type="text/plain")
