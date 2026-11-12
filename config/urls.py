from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin", admin.site.urls),
    path("", include("frontend.urls")),
    # Эндпоинты авторизации SimpleJWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Маршруты приложений
    path("api/users/", include("users.urls")),
    path("api/habits/", include("habits.urls")),
]
