from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Task





@receiver(post_save, sender=User)
def create_default_tasks(sender, instance, created, **kwargs):
    """
    Automatically create default tasks when a new user is created.

    This signal handler listens for the `post_save` signal sent by the `User` model. When a new user is created, it triggers 
    the creation of a set of default tasks for the user. These tasks are intended to provide the user with an initial set of 
    to-do items, done items, and in-progress items.

    Parameters
    ----------
    sender : Model
        The model class that sent the signal (in this case, the `User` model).
    instance : User
        The actual instance of the model that was saved.
    created : bool
        A boolean indicating whether a new record was created.
    **kwargs : dict
        Additional keyword arguments.
    """
    if created:
        Task.objects.create(user=instance, title='Get to work', status='todo')
        Task.objects.create(user=instance, title='Pick up groceries', status='todo')
        Task.objects.create(user=instance, title='Brush teeth', status='done')
        Task.objects.create(user=instance, title='Take a shower', status='done')
        Task.objects.create(user=instance, title='Check e-mail', status='done')
        Task.objects.create(user=instance, title='read a book', status='progress')
        Task.objects.create(user=instance, title='Walking', status='progress')