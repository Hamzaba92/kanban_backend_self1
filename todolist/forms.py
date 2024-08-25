from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    """
    Form for registering a new user with additional fields.

    This form extends Django's built-in `UserCreationForm` to include additional fields for first name, last name, 
    and email. The form is used to collect and validate data for user registration, ensuring that all required fields 
    are filled out correctly.

    Attributes
    ----------
    first_name : CharField
        The first name of the user. This field is required and has a maximum length of 30 characters.
    last_name : CharField
        The last name of the user. This field is required and has a maximum length of 30 characters.
    email : EmailField
        The email address of the user. This field is required and must be a valid email address with a maximum 
        length of 254 characters.
    """
    first_name = forms.CharField(max_length=30, required=True, help_text='First Name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Last Name')
    email = forms.EmailField(max_length=254, required=True, help_text='Enter a valid email address')

    class Meta:
        """
        Meta class to specify the model and fields used in the form.

        The form is based on the `User` model and includes fields for username, first name, last name, email, 
        password1, and password2. These fields correspond to the attributes of the `User` model and the built-in 
        `UserCreationForm`.
        """
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']