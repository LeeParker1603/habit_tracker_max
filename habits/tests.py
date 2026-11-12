from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitTestCase(APITestCase):

    def setUp(self):
        # Создаем тестовых пользователей
        self.user = User.objects.create_user(
            email="test@user.com", password="password123"
        )
        self.other_user = User.objects.create_user(
            email="other@user.com", password="password123"
        )

        # Генерируем JWT-токен для авторизации запросов
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "test@user.com", "password": "password123"},
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Создаем базовую приятную привычку для тестов связывания
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time="08:00:00",
            action="Принять пенную ванну",
            is_pleasant=True,
            duration=60,
        )

    def test_create_habit(self):
        """Тест успешного создания привычки"""
        url = reverse("habit_create")
        data = {
            "place": "Спортзал",
            "time": "07:00:00",
            "action": "Сделать зарядку",
            "duration": 90,
            "periodicity": 1,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(action="Сделать зарядку").count(), 1)

    def test_validator_reward_and_associated_habit(self):
        """Тест валидатора: нельзя одновременно указывать награду и связанную привычку"""
        url = reverse("habit_create")
        data = {
            "place": "Дом",
            "time": "19:00:00",
            "action": "Почитать книгу",
            "associated_habit": self.pleasant_habit.id,
            "reward": "Съесть шоколадку",
            "duration": 60,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Нельзя одновременно заполнять вознаграждение и связанную привычку.",
            str(response.data),
        )

    def test_validator_duration_limit(self):
        """Тест валидатора: длительность привычки не более 120 секунд"""
        url = reverse("habit_create")
        data = {
            "place": "Улица",
            "time": "12:00:00",
            "action": "Пробежка",
            "duration": 150,  # Больше 120 секунд
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_owner_isolation(self):
        """Тест изоляции данных: пользователь не видит чужие приватные привычки"""
        # Создаем приватную привычку от лица другого пользователя
        _ = Habit.objects.create(
            user=self.other_user,
            place="Офис",
            time="10:00:00",
            action="Чужая тайная привычка",
            duration=30,
        )

        url = reverse("habit_list")
        response = self.client.get(url)

        # В списке привычек текущего пользователя чужой привычки быть не должно
        self.assertEqual(
            response.status_code,
            (
                status.HTTP_200_RESULTS
                if hasattr(status, "HTTP_200_RESULTS")
                else status.HTTP_200_OK
            ),
        )
        actions = [habit["action"] for habit in response.data.get("results", [])]
        self.assertNotIn("Чужая тайная привычка", actions)
