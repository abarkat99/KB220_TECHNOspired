from django.db.models import Count
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseNotFound, Http404, HttpResponseRedirect, JsonResponse
from django.views.generic import TemplateView, CreateView, UpdateView, View
from django.contrib.auth.views import LoginView

# from accounts.forms import NewTempUserForm, NewStudentForm, NewMassStudentForm
# from accounts.models import Student, DepartmentMember, TempUser, StudentTempUser

from redressal.models import SubCategory

import datetime

from .constants import STATUS_DISPLAY_CONVERTER, STATUS_COLOR_CONVERTER
from .forms import NewGrievanceForm, NewReplyForm
from .models import DayToken, Grievance, Reply
from .filters import StudentGrievanceFilter, FilteredListView

# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils.crypto import salted_hmac
# import six
# import random
# from django.utils import timezone
# import pandas as pd
#
# from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.decorators import login_required


# def home(request):
#     if request.user.is_authenticated:
#         return redirect('dash_home')
#     return render(request, 'home.html')


class HomeView(LoginView):
    template_name = 'studentg/home.html'

'''
def faq(request):
    return render(request, 'faq.html')
    '''


# @login_required
# def dash_home(request):
#     return render(request, 'dash_home.html')


class DashboardView(TemplateView):
    template_name = 'studentg/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grievances = Grievance.objects.filter(user=self.request.user).order_by('-last_update')[:10]
        context['grievances'] = grievances
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


class CreateGrievance(CreateView):
    model = Grievance
    form_class = NewGrievanceForm
    template_name = 'studentg/add_grievance.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        grievance_save_helper(self.request, self.object)
        self.object.daytoken = DayToken.get_new_token()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class EditDraftGrievance(UpdateView):
    model = Grievance
    form_class = NewGrievanceForm
    template_name = 'studentg/edit_grievance.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        try:
            return Grievance.get_from_token(self.kwargs['token'])
        except Grievance.MultipleObjectsReturned:
            raise Http404()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        grievance_save_helper(self.request, self.object)
        self.object.date = datetime.date.today()
        self.object.daytoken = DayToken.get_new_token()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ViewGrievance(View):
    template_name = 'studentg/view_grievance.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        replies = context['replies']
        last_reply = replies.last()
        if last_reply and self.request.user != last_reply.user and grievance.status not in [Grievance.RESOLVED, Grievance.REJECTED]:
            reply_form = NewReplyForm()
            context['reply_form'] = reply_form
        grievance = context['grievance']
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        grievance = context['grievance']
        reply_form = NewReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.user = request.user
            reply.grievance = grievance
            reply.save()
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


class ViewGrievanceMessages(TemplateView):
    template_name = 'common/view_messages_modal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grievance = Grievance.get_from_token(kwargs['token'])
        replies = Reply.objects.filter(grievance=grievance)
        last_reply = replies.last()
        if last_reply and self.request.user != last_reply.user and grievance.status not in [Grievance.RESOLVED, Grievance.REJECTED]:
            allow_reply = True
        context['grievance'] = grievance
        context['replies'] = replies
        return context


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


# def addgrievance(request):
#     if request.method == 'POST':
#         form = NewGrievanceForm(request.POST, request.FILES)
#         if form.is_valid():
#             grievance = form.save(commit=False)
#             grievance.user = request.user
#             r_body = request.user.get_redressal_body()
#             if grievance.category != Grievance.DEPARTMENT:
#                 r_body = r_body.department.institute.redressal_body
#                 if grievance.category != Grievance.INSTITUTE:
#                     r_body = r_body.institute.university.redressal_body
#                     if grievance.category != Grievance.UNIVERSITY:
#                         raise Http404
#             grievance.redressal_body = r_body
#             grievance.daytoken = DayToken.get_new_token()
#             grievance.save()
#         return redirect('my_grievances')
#     else:
#         form = NewGrievanceForm()
#     return render(request, 'addgrievance.html', {'form': form})


# def load_subcategories(request):
#     category = request.GET.get('category')
#     r_body = request.user.get_redressal_body()
#     if category != Grievance.DEPARTMENT:
#         r_body = r_body.department.institute.redressal_body
#         if category != Grievance.INSTITUTE:
#             r_body = r_body.institute.university.redressal_body
#             if category != Grievance.UNIVERSITY:
#                 raise Http404()
#     subcats = SubCategory.objects.filter(
#         redressal_body=r_body).order_by('sub_type')
#     return render(request, 'subcat_options.html', {'subcats': subcats})


# def my_grievances(request):
#     grievance_list = Grievance.objects.filter(
#         user=request.user).order_by('-last_update')
#     page = request.GET.get('page', 1)
#     paginator = Paginator(grievance_list, 10)
#     try:
#         grievance_list = paginator.page(page)
#     except PageNotAnInteger:
#         grievance_list = paginator.page(1)
#     except EmptyPage:
#         grievance_list = paginator.page(paginator.num_pages)
#     return render(request, 'my_grievances.html', {'grievance_list': grievance_list, 'paginator': paginator})
#
#
# def getgrievance(request, token):
#     date = datetime.datetime.strptime(token[:-4], "%Y%m%d").date()
#     daytoken = int(token[-4:])
#     grievance = get_object_or_404(Grievance, date=date, daytoken=daytoken)
#     if request.method == 'POST':
#         reply_form = NewReplyForm(request.POST)
#         if reply_form.is_valid():
#             reply = reply_form.save(commit=False)
#             reply.user = request.user
#             reply.save()
#     replies = Reply.objects.filter(grievance=grievance)
#     reply_form = None
#     if request.user != grievance.user:
#         raise Http404()
#     if replies:
#         if request.user != replies.last().user and grievance.status != 'Resolved':
#             reply_form = NewReplyForm(initial={'grievance': grievance})
#     return render(request, 'getgrievance.html',
#                   {'grievance': grievance, 'replies': replies, 'token': token, 'reply_form': reply_form})

'''
def contact(request):
    return render(request, "contact.html")


def about_us(request):
    return render(request, "about_us.html")
    '''

