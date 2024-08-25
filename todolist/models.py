from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    """
    Model representing a task in the system.

    This model stores information about tasks, including their title, status, the user who created the task, and 
    the user to whom the task is assigned. The model also defines the behavior for what happens when a user associated 
    with a task is deleted.

    Attributes
    ----------
    title : CharField
        The title or name of the task.
    status : CharField
        The current status of the task, such as 'todo', 'done', or 'in progress'.
    user : ForeignKey
        The user who created the task. If the user is deleted, the task is also deleted (`on_delete=models.CASCADE`).
    assigned_to : ForeignKey
        The user to whom the task is assigned. If the assigned user is deleted, the assignment is set to NULL 
        (`on_delete=models.SET_NULL`), but the task itself remains in the system.
    """
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_tasks', blank=True, null=True)

    def __str__(self):
        """
        String representation of the Task model.

        Returns
        -------
        str
            The title of the task.
        """
        return self.title