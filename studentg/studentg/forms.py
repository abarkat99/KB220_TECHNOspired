from django import forms
from .models import Grievance, Reply, Rating
from redressal.models import SubCategory
from .constants import STATUS_VISIBLE_TO_COMMITTEE
from better_profanity import profanity

class NewGrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['category', 'sub_category', 'subject', 'message', 'image']

    def clean_subject(self):
        data = self.cleaned_data['subject']
        if profanity.contains_profanity(data):
            raise forms.ValidationError("Your Subject contains profanity!")
        return data

    def clean_message(self):
        data = self.cleaned_data['message']
        if profanity.contains_profanity(data):
            raise forms.ValidationError("Your message contains profanity!")
        return data

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(NewGrievanceForm, self).__init__(*args, **kwargs)
        self.fields['sub_category'].queryset = SubCategory.objects.none()
        if kwargs['instance']:
            self.fields['sub_category'].queryset = kwargs['instance'].redressal_body.subcategories
        if 'category' in self.data:
            try:
                category = int(self.data.get('category'))
                redressal_body = user.get_redressal_body().department
                if category != Grievance.DEPARTMENT:
                    redressal_body = redressal_body.institute
                    if category != Grievance.INSTITUTE:
                        redressal_body = redressal_body.university
                        if category != Grievance.UNIVERSITY:
                            raise ValueError
                redressal_body = redressal_body.redressal_body
                self.fields['sub_category'].queryset = redressal_body.subcategories
            except (ValueError, TypeError):
                pass


class GrievanceUpdateForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['status']
    
    status = forms.ChoiceField(choices=STATUS_VISIBLE_TO_COMMITTEE)


class GrievanceEscalationForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['sub_category']

    def __init__(self, *args, **kwargs):
        redressal_body = kwargs.pop('redressal_body')
        super(GrievanceEscalationForm, self).__init__(*args, **kwargs)
        self.fields['sub_category'].queryset = SubCategory.objects.filter(redressal_body=redressal_body)


class NewReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['message']

    def clean_message(self):
        data = self.cleaned_data['message']
        if profanity.contains_profanity(data):
            raise forms.ValidationError("Your message contains profanity!")
        return data


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']

    rating = forms.ChoiceField(choices=Rating.RATING_CHOICES, widget=forms.RadioSelect)
