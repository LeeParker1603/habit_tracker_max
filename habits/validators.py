from rest_framework.serializers import ValidationError


class HabitValidator:
    def __call__(self, attrs):
        is_pleasant = attrs.get("is_pleasant", False)
        associated_habit = attrs.get("associated_habit")
        reward = attrs.get("reward")
        duration = attrs.get("duration")
        periodicity = attrs.get("periodicity")

        # 1. Исключить одновременный выбор связанной привычки и указания вознаграждения
        if associated_habit and reward:
            raise ValidationError(
                "Нельзя одновременно заполнять вознаграждение и связанную привычку. Выберите что-то одно."
            )

        # 2. Время выполнения должно быть не больше 120 секунд
        if duration and duration > 120:
            raise ValidationError("Время на выполнение не должно превышать 120 секунд.")

        # 3. В связанные привычки могут попадать только привычки с признаком приятной привычки
        if associated_habit and not associated_habit.is_pleasant:
            raise ValidationError(
                "Связанная привычка обязательно должна быть приятной (is_pleasant=True)."
            )

        # 4. У приятной привычки не может быть вознаграждения или связанной привычки
        if is_pleasant:
            if reward or associated_habit:
                raise ValidationError(
                    "У приятной привычки не может быть вознаграждения или связанной привычки."
                )

        # 5. Нельзя выполнять привычку реже, чем 1 раз в 7 дней (период от 1 до 7 дней)
        if periodicity and (periodicity < 1 or periodicity > 7):
            raise ValidationError(
                "Периодичность выполнения привычки должна быть в диапазоне от 1 до 7 дней включительно."
            )
