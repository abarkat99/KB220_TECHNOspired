from .models import Grievance
from redressal.models import SubCategory
import django_filters
from redressal.filters import RedressalGrievanceFilter, FilteredListView


def sub_cats(request):
    category = request.GET.get('category')
    if category:
        category = int(category)
        redressal_body = request.user.get_redressal_body().department
        if category != Grievance.DEPARTMENT:
            redressal_body = redressal_body.institute
            if category != Grievance.INSTITUTE:
                redressal_body = redressal_body.university
                if category != Grievance.UNIVERSITY:
                    return SubCategory.objects.none()
        redressal_body = redressal_body.redressal_body
        return SubCategory.objects.filter(redressal_body=redressal_body)
    return SubCategory.objects.none()


class StudentGrievanceFilter(RedressalGrievanceFilter):
    sub_category = django_filters.ModelChoiceFilter(queryset=sub_cats)
    status = django_filters.ChoiceFilter(choices=Grievance.STATUS_CHOICES)

    class Meta:
        model = Grievance
        fields = ['subject', 'category', 'sub_category', 'status']
