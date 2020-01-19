from django import forms
from .models import Redressal_Body

class NewRedressalBodyForm(forms.ModelForm):
    class Meta:
        model = Redressal_Body
        fields = ['name']