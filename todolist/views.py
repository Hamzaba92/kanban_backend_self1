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

@method_decorator(csrf_exempt, name='dispatch')

class RegisterView(View):
    def post(self, request):
        try:
            # JSON-Daten aus dem Request-Body laden
            data = json.loads(request.body)

            # Registrierungsformular mit den gesendeten Daten initialisieren
            form = UserCreationForm({
                'username': data.get('username', ''),
                'password1': data.get('password1', ''),
                'password2': data.get('password2', '')
            })

            # Überprüfung der Gültigkeit des Formulars
            if form.is_valid():
                user = form.save(commit=False)
                user.first_name = data.get('first_name', '')
                user.last_name = data.get('last_name', '')
                user.email = data.get('email', '')
                user.save()

                return JsonResponse({'message': 'User registered successfully'}, status=201)
            else:
                # Rückgabe der Formularfehler als JSON-Antwort
                return JsonResponse({'errors': form.errors}, status=400)

        except KeyError as e:
            # Fehlermeldung, wenn ein erforderliches Feld fehlt
            return JsonResponse({'error': f'Missing field {str(e)}'}, status=400)
        except Exception as e:
            # Allgemeine Fehlermeldung
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