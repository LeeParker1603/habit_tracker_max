import json
import os

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

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

    # 2. Для всех остальных событий пока просто отвечаем "ok"
    return HttpResponse("ok", content_type="text/plain")
