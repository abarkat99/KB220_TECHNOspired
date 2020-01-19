from django import forms
from .models import Temp_User

class NewTempUserForm(forms.ModelForm):
    class Meta:
        model = Temp_User
        fields = ['first_name', 'last_name', 'email']