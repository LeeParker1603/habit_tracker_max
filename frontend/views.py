import os

from django.shortcuts import render


def index_view(request):
    return render(request, "index.html", {"vk_group_id": os.getenv("VK_ID", "")})
