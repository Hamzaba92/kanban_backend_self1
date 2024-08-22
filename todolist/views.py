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
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

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


def csrf_token_view(request):
    return JsonResponse({'csrfToken': get_token(request)})



@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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
        try:
            title = request.data.get('title')
            if not title:
                return Response({"error": "Title is required"}, status=status.HTTP_400_BAD_REQUEST)


            task = Task.objects.create(title=title, status='todo')
            
            serializer = TaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class TaskListView(ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(user=user)
        else:
            return Task.objects.none()




