from django.urls import path

from users.views import UserRegisterView

from .views import vk_callback

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="user_register"),
    path("vk/callback/", vk_callback, name="vk-callback"),
    path("vk/callback", vk_callback),
]
