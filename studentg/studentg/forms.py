from django import forms
from .models import Grievance

class NewGrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['category','sub_category','subject','message','image']