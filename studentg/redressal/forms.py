from django import forms
from django.core.exceptions import ValidationError

from .models import RedressalBody, SubCategory


class NewRedressalBodyForm(forms.ModelForm):
    class Meta:
        model = RedressalBody
        fields = ['name']


class NewSubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['sub_type']

    def clean_sub_type(self):
        sub_type = self.cleaned_data['sub_type']
        if SubCategory.objects.filter(sub_type=sub_type).exists():
            raise ValidationError("Subcategory already exists")
        return sub_type