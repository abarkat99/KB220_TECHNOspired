from django import forms
from .models import Redressal_Body,Sub_Category

class NewRedressalBodyForm(forms.ModelForm):
    class Meta:
        model = Redressal_Body
        fields = ['name']

class NewSubCategoryForm(forms.ModelForm):
    class Meta:
        model=Sub_Category
        fields=['sub_type']