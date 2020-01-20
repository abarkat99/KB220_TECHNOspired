from django import forms
from .models import Temp_User,User
from django.contrib.auth.forms import UserCreationForm

class NewTempUserForm(forms.ModelForm):
    class Meta:
        model = Temp_User
        fields = ['first_name', 'last_name', 'email']

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')