from celery import shared_task
from education.models import course
from users.models import User
from django.utils import timezone
from datetime import timedelta


@shared_task
def update_lesson(pk, model):
    if model == 'course':
        instance = course.objects.filter(pk=pk).first()

    if instance:
        count_lesson = instance.lessons.count

        if count_lesson > 0:
            print('Курс ' + instance.name + ' содержит ' + str(count_lesson) + ' уроков ')

@shared_task
def deactivate_inactive_users():
    month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=month_ago, is_active=True)
    inactive_users.update(is_active=False)