from studentg.models import Grievance
from .models import Sub_Category
import django_filters

def sub_cats(request):
    return Sub_Category.objects.filter(redressal_body=request.user.sys_user.get_redressal_body())
class GrievanceFilter(django_filters.FilterSet):
    sub_category=django_filters.ModelChoiceFilter(queryset=sub_cats)
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('last_update', 'last_update'),
            ('sub_category', 'sub_category'),
        ),

        # labels do not need to retain order
        field_labels={
            'last_update': 'Last Update',
            'sub_category': 'Sub Category'
        }
    )
    class Meta:
        model = Grievance
        fields = {'subject':['icontains', ], 'sub_category':['exact', ], }
    def __init__(self, *args, **kwargs):
       super(GrievanceFilter, self).__init__(*args, **kwargs)
       self.filters['subject__icontains'].label="Subject"
