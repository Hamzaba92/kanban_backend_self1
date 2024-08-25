from django.contrib import admin
from .models import Task



class TaskAdmin(admin.ModelAdmin):
    """
    Custom admin class for managing Task model in the Django admin site.

    This class allows the Task model to be managed with additional configurations 
    in the Django admin interface. Administrators can add, edit, delete, and view tasks.
    """
    pass

admin.site.register(Task, TaskAdmin)