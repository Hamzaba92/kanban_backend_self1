
from django.contrib import admin
from django.urls import path
from todolist.views import RegisterView, TaskCreateView, TaskListView, UserProfileView,  get_csrf_token
from todolist.views import login_view
from todolist.views import TaskCreateView, TaskUpdateView, TaskDeleteView

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/csrf-token/', get_csrf_token, name='csrf-token'),
    path('api/login/', login_view, name='login'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    path('loadTasks/', TaskListView.as_view(), name='task-list'),
    path('api/getusername/', UserProfileView.as_view(), name='getusername-for-greet')
]
