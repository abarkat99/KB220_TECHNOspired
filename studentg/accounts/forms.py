from django import forms
from .models import Temp_User,User,Student_Temp_User
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory

class NewTempUserForm(forms.ModelForm):
    class Meta:
        model = Temp_User
        fields = ['first_name', 'last_name', 'email']

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class NewStudentForm(forms.ModelForm):
    class Meta:
        model=Student_Temp_User
        fields=('rollno',)

class NewMassStudentForm(forms.Form):
    file=forms.FileField(allow_empty_file=False)