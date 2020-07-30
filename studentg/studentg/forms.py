from django import forms
from .models import Grievance, Reply
from redressal.models import SubCategory
from .constants import STATUS_VISIBLE_TO_COMMITTEE

class NewGrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['category', 'sub_category', 'subject', 'message', 'image']

    sub_category = forms.ModelChoiceField(queryset=SubCategory.objects.none())

    def __init__(self, *args, **kwargs):
        super(NewGrievanceForm, self).__init__(*args, **kwargs)
        if kwargs['instance']:
            self.fields['sub_category'].queryset = kwargs['instance'].redressal_body.subcategories


class GrievanceUpdateForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['status']
    
    status = forms.ChoiceField(choices=STATUS_VISIBLE_TO_COMMITTEE)


class NewReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['message']
