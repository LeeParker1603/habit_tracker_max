from django.urls import path

from habits.views import (
    HabitCreateAPIView,
    HabitRetrieveUpdateDestroyAPIView,
    PublicHabitListAPIView,
    UserHabitListAPIView,
)

urlpatterns = [
    path("", UserHabitListAPIView.as_view(), name="habit_list"),
    path("public/", PublicHabitListAPIView.as_view(), name="public_habit_list"),
    path("create/", HabitCreateAPIView.as_view(), name="habit_create"),
    path("<int:pk>/", HabitRetrieveUpdateDestroyAPIView.as_view(), name="habit_detail"),
]
