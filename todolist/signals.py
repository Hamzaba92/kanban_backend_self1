from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Task






@receiver(post_save, sender=User)
def create_default_tasks(sender, instance, created, **kwargs):
    if created:
        Task.objects.create(user=instance, title='Get to work', status='todo')
        Task.objects.create(user=instance, title='Pick up groceries', status='todo')
        Task.objects.create(user=instance, title='Brush teeth', status='done')
        Task.objects.create(user=instance, title='Take a shower', status='done')
        Task.objects.create(user=instance, title='Check e-mail', status='done')
        Task.objects.create(user=instance, title='read a book', status='progress')
        Task.objects.create(user=instance, title='Walking', status='progress')