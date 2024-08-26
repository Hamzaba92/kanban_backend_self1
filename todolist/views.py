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
from django.contrib.auth.models import User


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    """
    API View to handle user registration.

    This view handles the registration of a new user. It processes a POST request containing user details such as 
    username, password, first name, last name, and email. The view uses Django's `UserCreationForm` to validate 
    and create the user. The CSRF protection is disabled for this view using the `csrf_exempt` decorator.
    """

    def post(self, request):
        """
        Handle POST request to register a new user.

        This method processes the registration data sent in the request body as JSON. It uses the `UserCreationForm` 
        to validate the user data. If the form is valid, a new user is created and saved. If there are validation errors 
        or missing fields, appropriate error responses are returned.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object containing the registration data.

        Returns
        -------
        JsonResponse
            A JSON response indicating the result of the registration:
            - On success: Returns a 201 status with a success message.
            - On validation errors: Returns a 400 status with error details.
            - On missing fields: Returns a 400 status with a specific error message.
            - On any other exception: Returns a 500 status with an error message.
        """
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
    """
    Handle GET request to provide a CSRF token.

    This view returns a CSRF token in the response, ensuring that the CSRF cookie is set. The CSRF token is typically 
    used in subsequent requests that require CSRF protection.

    The view is decorated with `@ensure_csrf_cookie` to ensure that the CSRF cookie is set in the user's browser if it 
    is not already present. It is also decorated with `@api_view(["GET"])` to ensure that only GET requests are allowed.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    JsonResponse
        A JSON response containing the CSRF token. The response includes a key `csrfToken` with the token as its value.
    """
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


@csrf_protect
def login_view(request):
    """
    Handle user login requests.

    This view processes POST requests to authenticate a user with a username and password. If the credentials are valid, 
    the user is logged in and a default task is created if none exist for the user. The view returns a success message 
    on successful login, or an error message if the credentials are invalid or if the request method is not POST.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object containing the request data.

    Returns
    -------
    JsonResponse
        A JSON response with a success message if login is successful, or an error message with the appropriate 
        HTTP status code if login fails or if the request method is invalid.
    """
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
    """
    API View to delete an existing task.

    This view handles the deletion of an existing task. The task is identified by its primary key (`pk`). 
    If the task is found, it is deleted and a success message is returned. If the task does not exist, 
    a 404 Not Found response is returned.
    """
    def delete(self, request, pk, *args, **kwargs):
        """
        Handle DELETE request to remove an existing task.

        This method attempts to delete a task identified by the provided primary key (`pk`). If the task is successfully 
        deleted, a confirmation message is returned. If the task is not found, a 404 Not Found response is returned.

        Parameters
        ----------
        request : Request
            The HTTP request object.
        pk : int
            The primary key of the task to be deleted.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            A Response object containing a success message if the task is deleted successfully. If the task is not found,
            a 404 Not Found response is returned.
        """
        try:
            task = Task.objects.get(pk=pk)
            task.delete()
            return Response({"message": "Task deleted successfully"}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


        

class TaskUpdateView(APIView):
    """
    API View to update an existing task.

    This view handles updating an existing task's details. The user can update the task's title, status, and the user 
    to whom the task is assigned. If the task or assigned user does not exist, appropriate error responses are returned.
    """
    def put(self, request, pk, *args, **kwargs):
        """
        Handle PUT request to update an existing task.

        This method attempts to update a task with the provided primary key (`pk`). It updates the task's fields with the
        data provided in the request. If the `assigned_to` field is provided, it checks if the user exists and assigns 
        the task to that user.

        Parameters
        ----------
        request : Request
            The HTTP request object containing the updated task data.
        pk : int
            The primary key of the task to be updated.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            A Response object containing the serialized task data if the update is successful.
            If the task or assigned user is not found, a 404 Not Found response is returned.
            If the data is invalid, a 400 Bad Request response is returned.
        """
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        assigned_to_id = request.data.get('assigned_to')
        if assigned_to_id:
            try:
                assigned_to = User.objects.get(id=assigned_to_id)
                task.assigned_to = assigned_to
            except User.DoesNotExist:
                return Response({"error": "Assigned user not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class TaskCreateView(APIView):
    """
    API View to create a new task.

    This view handles the creation of a new task for the authenticated user. It requires the user to be authenticated,
    and it validates the presence of a task title. Optionally, the task can be assigned to another user if a valid 
    `assigned_to` user ID is provided.

    Methods
    -------
    post(request):
        Handles the POST request to create a new task. Returns a JSON response with the created task data if successful, 
        or an error message with the appropriate HTTP status code.

    Example
    -------
    POST /api/tasks/
    {
        "title": "Finish project report",
        "assigned_to": 3
    }

    Possible Responses
    ------------------
    - 201 Created: Task successfully created
    - 400 Bad Request: Missing title in the request data
    - 401 Unauthorized: User is not authenticated
    - 404 Not Found: Assigned user does not exist
    """
    def post(self, request):
        """
        .. :no-index:

        Handle POST request to create a new task.

        The request must contain a 'title' in the data. If the 'assigned_to' field is provided, it should correspond
        to a valid user ID. The task is created with a default status of 'todo' and is associated with the authenticated user.

        Parameters
        ----------
        request : Request
            The request object containing the data for the new task, including 'title' and optionally 'assigned_to'.

        Returns 
        -------
        Response
            A Response object containing the serialized task data with a status code of 201 on success, or an error message
            with the corresponding status code on failure.

        Errors
        ------
        - 401 Unauthorized: Returned if the user is not authenticated.
        - 400 Bad Request: Returned if the 'title' field is missing.
        - 404 Not Found: Returned if the 'assigned_to' user ID does not exist.
        """
        if not request.user.is_authenticated:
            return Response({'error': 'User is not authenticated'},
                            status=status.HTTP_401_UNAUTHORIZED)

        title = request.data.get('title')
        assigned_to_id = request.data.get('assigned_to')

        if not title:
            return Response({'error': 'Title is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        assigned_to = None
        if assigned_to_id:
            try:
                assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                return Response({'error': 'Assigned user not found'},
                                status=status.HTTP_404_NOT_FOUND)

        task = Task.objects.create(title=title, status='todo',
                                   user=request.user,
                                   assigned_to=assigned_to)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


        


class TaskListView(ListAPIView):
    """
    API View to list tasks for the authenticated user.

    This view returns a list of tasks that belong to the authenticated user or are assigned to them. The view uses the 
    `TaskSerializer` to serialize the task data.

    Attributes
    ----------
    serializer_class : TaskSerializer
        Specifies the serializer class to be used for the task data.

    Methods
    -------
    get_queryset()
        Retrieves the queryset of tasks for the authenticated user, including tasks created by the user or assigned to the user.
    get(request, *args, **kwargs)
        Handles the GET request to return the serialized list of tasks for the authenticated user.
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Retrieve the queryset of tasks for the authenticated user.

        This method filters tasks based on the authenticated user. It includes tasks that the user has created 
        as well as tasks that are assigned to the user.

        Returns
        -------
        QuerySet
            A queryset containing tasks related to the authenticated user. Returns an empty queryset if the user 
            is not authenticated.
        """
        user = self.request.user
        if user.is_authenticated:
            tasks = Task.objects.filter(user=user) | Task.objects.filter(assigned_to=user)
            return tasks
        else:
            print("User not authenticated or no tasks found")
            return Task.objects.none()

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to return the list of tasks for the authenticated user.

        This method retrieves the queryset of tasks using `get_queryset`, serializes the data using the specified 
        serializer, and returns the serialized data as a JSON response.

        Parameters
        ----------
        request : Request
            The HTTP request object.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            A Response object containing the serialized task data for the authenticated user.

        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




class UserProfileView(APIView):
    """
    API View to retrieve the authenticated user's profile information.

    This view handles GET requests to retrieve basic profile information (first name and last name) of the authenticated user.
    The view is protected by authentication, meaning only authenticated users can access this endpoint.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request to return the authenticated user's profile data.

        This method retrieves the first name and last name of the authenticated user from the request object and 
        returns it in the response.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object, which contains the authenticated user's information.

        Returns
        -------
        Response
            A JSON response containing the user's first name and last name.
        """
        profile_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        return Response(profile_data)
    

class UserListView(APIView):
    """
    API View to retrieve a list of all users.

    This view handles GET requests to retrieve a list of all users in the system. Each user's basic information, 
    including ID, first name, and last name, is returned in the response. The view is protected by authentication, 
    so only authenticated users can access this endpoint.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to return a list of all users.

        This method retrieves all user records from the database and serializes their ID, first name, and last name into 
        a list of dictionaries. The resulting list is then returned as a JSON response.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object, which contains the authenticated user's information.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            A JSON response containing a list of all users, where each user is represented by a dictionary with their ID, 
            first name, and last name.
        """
        users = User.objects.all()
        user_data = [
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
            for user in users
        ]
        return Response(user_data)
    



