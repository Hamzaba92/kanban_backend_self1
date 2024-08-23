from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views import View
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from rest_framework.generics import ListAPIView
from django.contrib.sessions.backends.db import SessionStore
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            form = UserCreationForm({
                'username': data.get('username', ''),
                'password1': data.get('password1', ''),
                'password2': data.get('password2', '')
            })

            if form.is_valid():
                user = form.save(commit=False)
                user.first_name = data.get('first_name', '')
                user.last_name = data.get('last_name', '')
                user.email = data.get('email', '')
                user.save()

                return JsonResponse({'message': 'User registered successfully'}, status=201)
            else:
                return JsonResponse({'errors': form.errors}, status=400)

        except KeyError as e:
            return JsonResponse({'error': f'Missing field {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

@api_view(["GET"])
@ensure_csrf_cookie
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


@csrf_protect
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if not Task.objects.filter(user=user).exists():
                Task.objects.create(user=user, title='Get to Work', status='todo')

            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)



class TaskDeleteView(APIView):
    def delete(self, request, pk, *args, **kwargs):
        try:
            task = Task.objects.get(pk=pk)
            task.delete()
            return Response({"message": "Task deleted successfully"}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        

class TaskUpdateView(APIView):
    def put(self, request, pk, *args, **kwargs):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TaskCreateView(APIView):

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        title = request.data.get('title')
        if not title:
            return Response({"error": "Title is required"}, status=status.HTTP_400_BAD_REQUEST)

        task = Task.objects.create(title=title, status='todo', user=request.user)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        


class TaskListView(ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            tasks = Task.objects.filter(user=user)
            return tasks
        else:
            print("User not authenticated or no tasks found")
            return Task.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        return Response(profile_data)