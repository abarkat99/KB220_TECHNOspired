import django_filters
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import ListView
from django_filters.constants import ALL_FIELDS
from django_filters.filterset import filterset_factory

from studentg.models import Grievance
from studentg.constants import STATUS_VISIBLE_TO_COMMITTEE
from .models import SubCategory


def sub_cats(request):
    return SubCategory.objects.filter(redressal_body=request.user.get_redressal_body())


class RedressalGrievanceFilter(django_filters.FilterSet):
    sub_category = django_filters.ModelChoiceFilter(queryset=sub_cats)
    subject = django_filters.CharFilter(lookup_expr='icontains', label='Subject')
    status = django_filters.ChoiceFilter(choices=STATUS_VISIBLE_TO_COMMITTEE)
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('last_update', 'last_update'),
            ('sub_category', 'sub_category'),
        ),

        # labels do not need to retain order
        field_labels={
            'last_update': 'Last Update',
            'sub_category': 'Sub Category',
        }
    )

    class Meta:
        model = Grievance
        fields = ['subject', 'sub_category', 'status']
        # fields = {'subject': ['icontains', ], 'sub_category': ['exact', ], 'status': ['exact', ]}

    # def __init__(self, *args, **kwargs):
    #     super(RedressalGrievanceFilter, self).__init__(*args, **kwargs)
    #     self.filters['subject__icontains'].label = "Subject"


class FilteredListView(ListView):
    filterset_class = None
    filterset_fields = ALL_FIELDS

    def get_filterset_class(self):
        """
        Returns the filterset class to use in this view
        """
        if self.filterset_class:
            return self.filterset_class
        elif self.model:
            return filterset_factory(model=self.model, fields=self.filterset_fields)
        else:
            msg = "'%s' must define 'filterset_class' or 'model'"
            raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = super(FilteredListView, self).get_queryset()
        filterset_class = self.get_filterset_class()
        self.filterset = filterset_class(data=self.request.GET, queryset=self.queryset, request=self.request)
        self.queryset = self.filterset.qs
        return super(FilteredListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(FilteredListView, self).get_context_data(**kwargs)
        context['filter_form'] = self.filterset.form
        return context