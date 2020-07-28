from django import forms
from .models import TempUser, User, StudentTempUser
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory


class NewTempUserForm(forms.ModelForm):
    class Meta:
        model = TempUser
        fields = ['first_name', 'last_name', 'email']


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class NewStudentForm(forms.ModelForm):
    class Meta:
        model = StudentTempUser
        fields = ('rollno',)


class NewMassStudentForm(forms.Form):
    file = forms.FileField(allow_empty_file=False)
