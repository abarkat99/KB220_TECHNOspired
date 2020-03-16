from django import forms
from .models import RedressalBody,SubCategory

class NewRedressalBodyForm(forms.ModelForm):
    class Meta:
        model = RedressalBody
        fields = ['name']

class NewSubCategoryForm(forms.ModelForm):
    class Meta:
        model=SubCategory
        fields=['sub_type']