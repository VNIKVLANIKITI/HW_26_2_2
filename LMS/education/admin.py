from django.contrib import admin
from users.models import User, Payment
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils import timezone

admin.site.register(User)
admin.site.register(Payment)

# Создаем или получаем расписание
schedule, created = IntervalSchedule.objects.get_or_create(
    every=30,
    period=IntervalSchedule.DAYS,
)

# Используем get_or_create для создания периодической задачи
task_name = 'Deactivate inactive users'
task, created = PeriodicTask.objects.get_or_create(
    interval=schedule,
    name=task_name,
    task='your_app_name.tasks.deactivate_inactive_users',
    defaults={'start_time': timezone.now()},
)

if created:
    print(f"Создана новая периодическая задача: {task_name}")
else:
    print(f"Периодическая задача уже существует: {task_name}")