from django.db.models import Count
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseNotFound, Http404, HttpResponseRedirect, JsonResponse
from django.views.generic import TemplateView, CreateView, UpdateView, View
from django.contrib.auth.views import LoginView


from redressal.models import SubCategory

import datetime

from .constants import STATUS_DISPLAY_CONVERTER, STATUS_COLOR_CONVERTER
from .decorators import is_owner_of_grievance
from .forms import NewGrievanceForm, NewReplyForm, RatingForm
from .models import DayToken, Grievance, Reply, Notification, Rating
from .filters import StudentGrievanceFilter, FilteredListView
from redressal.helpers import get_redressal_body_members

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class HomeView(LoginView):
    template_name = 'studentg/home.html'


@method_decorator(login_required, name="dispatch")
class DashboardView(TemplateView):
    template_name = 'studentg/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grievances = Grievance.objects.filter(user=self.request.user).order_by('-last_update')[:5]
        draft_count = Grievance.objects.filter(user=self.request.user, status=Grievance.DRAFT).count()
        notifications = Notification.objects.filter(user=self.request.user).order_by('-date_time')[:5]
        context['grievances'] = grievances
        context['notifications'] = notifications
        context['draft_count'] = draft_count
        return context


def grievance_save_helper(request, grievance):
    if 'draft_submit' in request.POST:
        grievance.status = Grievance.DRAFT
    elif 'true_submit' in request.POST:
        grievance.status = Grievance.REVIEW
    redressal_body = request.user.get_redressal_body().department
    if grievance.category != Grievance.DEPARTMENT:
        redressal_body = redressal_body.institute
        if grievance.category != Grievance.INSTITUTE:
            redressal_body = redressal_body.university
            if grievance.category != Grievance.UNIVERSITY:
                raise Http404()
    grievance.redressal_body = redressal_body.redressal_body


def grievance_notification_helper(grievance):
    if grievance.status == Grievance.REVIEW or grievance.status != grievance.DRAFT:
        for user in get_redressal_body_members(grievance.redressal_body):
            notification = Notification()
            notification.user = user
            notification.grievance = grievance
            notification.save()


@method_decorator(login_required, name="dispatch")
class CreateGrievance(CreateView):
    model = Grievance
    form_class = NewGrievanceForm
    template_name = 'studentg/add_grievance.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        print('hello')
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        grievance_save_helper(self.request, self.object)
        self.object.daytoken = DayToken.get_new_token()
        self.object.save()
        grievance_notification_helper(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(CreateGrievance, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


@method_decorator(login_required, name="dispatch")
@method_decorator(is_owner_of_grievance(raise_denied=True), name="dispatch")
class EditDraftGrievance(UpdateView):
    model = Grievance
    form_class = NewGrievanceForm
    template_name = 'studentg/edit_grievance.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        try:
            return Grievance.get_from_token(self.kwargs['token'])
        except Grievance.DoesNotExist:
            raise Http404()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        grievance_save_helper(self.request, self.object)
        self.object.date = datetime.date.today()
        self.object.daytoken = DayToken.get_new_token()
        self.object.save()
        grievance_notification_helper(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(EditDraftGrievance, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


@method_decorator(login_required, name="dispatch")
@method_decorator(is_owner_of_grievance(raise_denied=True), name="dispatch")
class ViewGrievance(View):
    template_name = 'studentg/view_grievance.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        grievance = context['grievance']
        replies = context['replies']
        last_reply = replies.last()
        if grievance.status in [Grievance.RESOLVED, Grievance.REJECTED]:
            try:
                rating_form = RatingForm(instance=grievance.rating)
            except Rating.DoesNotExist:
                rating_form = RatingForm()
            context['rating_form'] = rating_form
        if last_reply and self.request.user != last_reply.user and grievance.status not in [Grievance.RESOLVED, Grievance.REJECTED]:
            reply_form = NewReplyForm()
            context['reply_form'] = reply_form
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        grievance = context['grievance']
        replies = context['replies']
        last_reply = replies.last()
        reply_form = NewReplyForm(request.POST)
        if grievance.status in [Grievance.RESOLVED, Grievance.REJECTED]:
            try:
                rating_form = RatingForm(request.POST, instance=grievance.rating)
            except Rating.DoesNotExist:
                rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.grievance = grievance
                rating.save()
                return redirect('view_grievance', token=kwargs['token'])
            context['rating_form'] = rating_form
            return render(request, self.template_name, context)
        if last_reply and self.request.user != last_reply.user and grievance.status not in [Grievance.RESOLVED, Grievance.REJECTED]:
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.user = request.user
                reply.grievance = grievance
                reply.save()
                return redirect('view_grievance', token=kwargs['token'])
            context['reply_form'] = reply_form
            return render(request, self.template_name, context)
        return redirect('view_grievance', token=kwargs['token'])

    def get_context_data(self, **kwargs):
        context = {}
        grievance = Grievance.get_from_token(kwargs['token'])
        if not grievance:
            raise Http404()
        replies = Reply.objects.filter(grievance=grievance)
        context['grievance'] = grievance
        context['replies'] = replies
        return context


@method_decorator(login_required, name="dispatch")
class LoadSubcategories(TemplateView):
    template_name = 'studentg/subcat_options.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = int(self.request.GET.get('category'))
        except:
            raise Http404()
        redressal_body = self.request.user.get_redressal_body().department
        if category != Grievance.DEPARTMENT:
            redressal_body = redressal_body.institute
            if category != Grievance.INSTITUTE:
                redressal_body = redressal_body.university
                if category != Grievance.UNIVERSITY:
                    raise Http404()
        redressal_body = redressal_body.redressal_body
        subcategories = SubCategory.objects.filter(
            redressal_body=redressal_body).order_by('sub_type')
        context['subcategories'] = subcategories
        return context


@method_decorator(login_required, name="dispatch")
class AllGrievances(FilteredListView):
    template_name = 'studentg/all_grievances.html'
    filterset_class = StudentGrievanceFilter
    model = Grievance
    paginate_by = 10

    def get_queryset(self):
        self.queryset = Grievance.objects.filter(user=self.request.user)
        return super(AllGrievances, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required
def status_stats_chart(request):
    redressal_body = request.user.get_redressal_body()
    status_filtered = Grievance.objects.filter(user=request.user).order_by(
        'status').values('status').annotate(count=Count('id'))
    labels = []
    data = []
    backgroundColor = []
    for entry in status_filtered:
        labels.append(STATUS_DISPLAY_CONVERTER[entry['status']])
        backgroundColor.append(STATUS_COLOR_CONVERTER[entry['status']])
        data.append(entry['count'])
    data = {
        'labels': labels,
        'datasets': [
            {
                'backgroundColor': backgroundColor,
                'data': data,
            },
        ]
    }
    return JsonResponse(data=data)


def overall_status_stats_chart(request):
    status_filtered = Grievance.objects.exclude(status=Grievance.DRAFT).order_by(
        'status').values('status').annotate(count=Count('id'))
    labels = []
    data = []
    backgroundColor = []
    for entry in status_filtered:
        labels.append(STATUS_DISPLAY_CONVERTER[entry['status']])
        backgroundColor.append(STATUS_COLOR_CONVERTER[entry['status']])
        data.append(entry['count'])
    total_grievances = sum(data)
    data = list(map(lambda x: 100 * x / total_grievances, data))
    data = {
        'labels': labels,
        'datasets': [
            {
                'backgroundColor': backgroundColor,
                'data': data,
            },
        ]
    }
    return JsonResponse(data=data)
