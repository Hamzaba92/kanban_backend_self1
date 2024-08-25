from django.test import TestCase


from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Task

class TaskCreateViewTest(APITestCase):
    
    def setUp(self):
        # Setup initial data and user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('task-create')

    def test_create_task_success(self):
        self.client.login(username='testuser', password='testpass')

        data = {
            'title': 'New Task'
        }

        initial_count = Task.objects.count()
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), initial_count + 1)

    def test_create_task_with_assigned_user(self):
        self.client.login(username='testuser', password='testpass')

        assigned_user = User.objects.create_user(username='assigneduser', password='assignedpass')
        data = {
            'title': 'New Task',
            'assigned_to': assigned_user.id
        }

        initial_count = Task.objects.count()
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), initial_count + 1)
        self.assertEqual(Task.objects.last().assigned_to, assigned_user)
