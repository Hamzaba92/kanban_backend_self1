from rest_framework import serializers
from .models import Task
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer is used to convert User model instances into JSON representations. It includes basic fields such 
    as the user's ID, first name, and last name.
    """
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.

    This serializer is used to convert Task model instances into JSON representations. It includes fields such as 
    the task's ID, title, status, the user who created the task, and the user to whom the task is assigned. Additionally, 
    it provides a custom field `assigned_to_name` that returns the full name of the assigned user if available.
    """
    assigned_to = UserSerializer(read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'assigned_to', 'user', 'assigned_to_name']

    def get_assigned_to_name(self, obj):
        """
        Retrieve the full name of the user to whom the task is assigned.

        This method returns the first and last name of the assigned user as a single string. If no user is assigned, 
        it returns None.

        Parameters
        ----------
        obj : Task
            The Task instance being serialized.

        Returns
        -------
        str or None
            The full name of the assigned user, or None if no user is assigned.
        """
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None
