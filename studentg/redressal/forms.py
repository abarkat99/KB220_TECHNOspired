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

    def __init__(self, *args, **kwargs):
        self.redressal_body = kwargs.pop('redressal_body')
        super(NewSubCategoryForm, self).__init__(*args, **kwargs)

    def clean_sub_type(self):
        sub_type = self.cleaned_data['sub_type']
        if SubCategory.objects.filter(sub_type=sub_type, redressal_body=self.redressal_body).exists():
            raise ValidationError("Subcategory already exists")
        return sub_type