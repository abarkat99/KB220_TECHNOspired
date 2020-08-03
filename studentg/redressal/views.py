from datetime import datetime, timedelta

from accounts.forms import NewTempUserForm, NewStudentForm, NewMassStudentForm
from accounts.models import TempUser, StudentTempUser, User, UniversityMember, InstituteMember, DepartmentMember, \
    Student

from studentg.models import Grievance, Reply, Notification, Rating
from studentg.forms import GrievanceUpdateForm, NewReplyForm, GrievanceEscalationForm
from studentg.constants import STATUS_COLOR_CONVERTER, STATUS_DISPLAY_CONVERTER

from .decorators import is_committee_head, is_committee_member, is_committee_head_of_super_body_type, \
    is_committee_member_of_grievance, is_department_member, is_committee_head_of, is_committee_head_of_temp_user, \
    is_committee_head_of_super_body
from .filters import RedressalGrievanceFilter, FilteredListView
from .forms import NewRedressalBodyForm, NewSubCategoryForm, SelectSubCategoryForm
from .models import RedressalBody, University, Institute, Department, SubCategory

from django.views.generic import TemplateView, CreateView, View, FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, Http404, JsonResponse, HttpResponseRedirect
import json
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView

import pandas as pd
from django.utils import timezone

# Charts
from django.db.models import Count, Avg, F


class HomeView(LoginView):
    template_name = 'redressal/home.html'


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'redressal/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        redressal_body = self.request.user.get_redressal_body()
        grievances = Grievance.objects.filter(redressal_body=redressal_body).exclude(status=Grievance.DRAFT).order_by(
            '-last_update')[:3]
        notifications = Notification.objects.filter(user=self.request.user).order_by('-date_time')[:5]
        context['grievances'] = grievances
        context['notifications'] = notifications
        return context


@method_decorator(is_committee_head(raise_denied=True), name="dispatch")
class ViewSubcategories(CreateView):
    model = SubCategory
    form_class = NewSubCategoryForm
    template_name = "redressal/view_subcategories.html"
    success_url = reverse_lazy("view_subcategories")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.redressal_body = self.request.user.get_redressal_body()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subcategories = SubCategory.objects.filter(redressal_body=self.request.user.get_redressal_body())
        context['subcategories'] = subcategories
        return context

    def get_form_kwargs(self):
        kwargs = super(ViewSubcategories, self).get_form_kwargs()
        kwargs.update({'redressal_body': self.request.user.get_redressal_body()})
        return kwargs


@method_decorator(login_required, name="dispatch")
class AllGrievances(FilteredListView):
    template_name = 'redressal/all_grievances.html'
    filterset_class = RedressalGrievanceFilter
    model = Grievance
    paginate_by = 10

    def get_queryset(self):
        redressal_body = self.request.user.get_redressal_body()
        self.queryset = Grievance.objects.filter(redressal_body=redressal_body).exclude(status=Grievance.DRAFT)
        return super(AllGrievances, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@method_decorator(is_committee_member_of_grievance(raise_denied=True), name="dispatch")
class ViewGrievance(View):
    template_name = 'redressal/view_grievance.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        grievance = context['grievance']
        reply_form = NewReplyForm()
        update_form = GrievanceUpdateForm(instance=grievance)
        user_body_object = request.user.get_redressal_body().get_body_object()
        if user_body_object.IS_SUB_BODY:
            escalation_form = GrievanceEscalationForm(redressal_body=user_body_object.get_super_body(),
                                                      instance=grievance, prefix='escalation')
            context['escalation_form'] = escalation_form
        context['reply_form'] = reply_form
        context['update_form'] = update_form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        grievance = context['grievance']
        reply_form = NewReplyForm(request.POST)
        update_form = GrievanceUpdateForm(request.POST, instance=grievance)
        user_body_object = request.user.get_redressal_body().get_body_object()
        if user_body_object.IS_SUB_BODY:
            escalation_form = GrievanceEscalationForm(request.POST, redressal_body=user_body_object.get_super_body(),
                                                      instance=grievance, prefix='escalation')
            if escalation_form.is_valid():
                grievance = escalation_form.save(commit=False)
                category_escalator = {
                    Grievance.DEPARTMENT: Grievance.INSTITUTE,
                    Grievance.INSTITUTE: Grievance.DEPARTMENT
                }
                grievance.category = category_escalator[grievance.category]
                grievance.redressal_body = user_body_object.get_super_body()
                grievance.status = Grievance.REVIEW
                grievance.save()
                return redirect('all_grievances')
            context['escalation_form'] = escalation_form
        is_reply = False
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.user = request.user
            reply.grievance = grievance
            reply.save()
            is_reply = True
        if update_form.is_valid():
            old_status = grievance.status
            grievance = update_form.save()
            if old_status != grievance.status or is_reply:
                notification = Notification()
                notification.user = grievance.user
                notification.grievance = grievance
                notification.save()
        context['reply_form'] = reply_form
        context['update_form'] = update_form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {}
        grievance = Grievance.get_from_token(kwargs['token'])
        if not grievance or grievance.status == Grievance.DRAFT:
            raise Http404()
        replies = Reply.objects.filter(grievance=grievance)
        allow_reply = True
        context['grievance'] = grievance
        context['replies'] = replies
        return context


@method_decorator(is_committee_head(raise_denied=True), name="dispatch")
class ViewMembers(TemplateView):
    template_name = 'redressal/view_members.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members = self.request.user.get_designation_object().get_body_members()
        in_members = TempUser.objects.filter(redressal_body=self.request.user.get_redressal_body()).exclude(
            designation=TempUser.STUDENT)
        context['members'] = members
        context['in_members'] = in_members
        return context


@method_decorator(is_committee_head(raise_denied=True), name="dispatch")
class AddMember(CreateView):
    model = TempUser
    form_class = NewTempUserForm
    template_name = 'redressal/add_member.html'
    success_url = reverse_lazy("view_members")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.redressal_body = self.request.user.get_redressal_body()
        self.object.designation = self.request.user.designation[:-2]
        self.object.created_at = timezone.now()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(is_committee_head_of_temp_user(raise_denied=True), name="dispatch")
class DeleteInvitedMember(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            TempUser.objects.get(pk=pk).delete()
        except TempUser.DoesNotExist:
            raise Http404()
        return redirect('view_members')


@method_decorator(is_committee_head_of(raise_denied=True), name="dispatch")
class DeleteMember(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            User.objects.get(pk=pk).delete()
        except User.DoesNotExist:
            raise Http404()
        return redirect('view_members')


@method_decorator(is_committee_head_of_super_body_type(raise_denied=True), name="dispatch")
class ViewBodies(TemplateView):
    template_name = 'redressal/view_bodies.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bodies, in_bodies = self.request.user.get_redressal_body().get_body_object().get_sub_bodies()
        context['bodies'] = bodies
        context['in_bodies'] = in_bodies
        return context


@method_decorator(is_committee_head_of_super_body_type(raise_denied=True), name="dispatch")
class AddBody(View):
    template_name = "redressal/add_body.html"
    body_type = None

    UNIVERSITY = 'University'
    INSTITUTE = 'Institute'
    DEPARTMENT = 'Department'

    def get_body_type(self):
        if self.request.user.is_superuser:
            return self.UNIVERSITY
        if self.request.user.designation == User.UNI_HEAD:
            return 'Institute'
        if self.request.user.designation == User.INS_HEAD:
            return 'Department'
        return None

    def get(self, request, *args, **kwargs):
        rbody_form = NewRedressalBodyForm()
        tuser_form = NewTempUserForm()
        context = {
            'rbody_form': rbody_form,
            'tuser_form': tuser_form,
            'body_type': self.body_type,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        rbody_form = NewRedressalBodyForm(request.POST)
        tuser_form = NewTempUserForm(request.POST)
        if rbody_form.is_valid() and tuser_form.is_valid():
            rbody = rbody_form.save(commit=False)
            temp_user = tuser_form.save(commit=False)
            body_object = None
            if self.body_type == self.UNIVERSITY:
                rbody.body_type = RedressalBody.UNIVERSITY
                body_object = University()
                temp_user.designation = TempUser.UNI_HEAD
            elif self.body_type == self.INSTITUTE:
                rbody.body_type = RedressalBody.INSTITUTE
                body_object = Institute()
                body_object.university = request.user.universitymember.redressal_body.university
                temp_user.designation = TempUser.INS_HEAD
            elif self.body_type == self.DEPARTMENT:
                rbody.body_type = RedressalBody.DEPARTMENT
                body_object = Department()
                body_object.institute = request.user.institutemember.redressal_body.institute
                temp_user.designation = TempUser.DEP_HEAD
            rbody.save()
            body_object.redressal_body = rbody
            body_object.save()
            temp_user.redressal_body = rbody
            temp_user.created_at = timezone.now()
            temp_user.save()
            sub_cat = SubCategory()
            sub_cat.sub_type = "Other"
            sub_cat.redressal_body = rbody
            sub_cat.save()
            return redirect('view_bodies')
        context = {
            'rbody_form': rbody_form,
            'tuser_form': tuser_form,
            'body_type': self.body_type,
        }
        return render(request, self.template_name, context)

    def dispatch(self, request, *args, **kwargs):
        self.body_type = self.get_body_type()
        if self.body_type is None:
            raise Http404()
        return super(AddBody, self).dispatch(request, *args, **kwargs)


@method_decorator(is_committee_head_of_super_body(raise_denied=True), name="dispatch")
class DeleteBody(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            RedressalBody.objects.get(pk=pk).delete()
        except User.DoesNotExist:
            raise Http404()
        return redirect('view_bodies')


@method_decorator(is_department_member(raise_denied=True), name="dispatch")
class ViewStudents(TemplateView):
    template_name = 'redressal/view_students.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        redressal_body = self.request.user.get_redressal_body()
        students = Student.objects.filter(redressal_body=redressal_body)
        in_students = StudentTempUser.objects.filter(user__redressal_body=redressal_body)
        context['students'] = students
        context['in_students'] = in_students
        return context


@method_decorator(is_department_member(raise_denied=True), name="dispatch")
class AddStudent(FormView):
    template_name = 'redressal/add_student.html'
    form_class = NewMassStudentForm
    success_url = reverse_lazy('view_students')

    def form_valid(self, form):
        excel_file = self.request.FILES['file']
        data = pd.read_csv(excel_file)
        df = pd.DataFrame(
            data, columns=['First name', 'Last name', 'Email', 'Rollno'])
        for index, row in df.iterrows():
            tuser = TempUser()
            tuser.first_name = row['First name']
            tuser.last_name = row['Last name']
            tuser.email = row['Email']
            tuser.created_at = timezone.now()
            tuser.redressal_body = self.request.user.get_redressal_body()
            tuser.designation = TempUser.STUDENT
            tuser.save()
            stuser = StudentTempUser()
            stuser.rollno = row['Rollno']
            stuser.user = tuser
            stuser.save()
        return super(AddStudent, self).form_valid(form)


@is_committee_member(raise_denied=True)
def charts(request):
    redressal_body = request.user.get_redressal_body()
    base_queryset = Grievance.objects.filter(redressal_body=redressal_body)
    total_count = base_queryset.count()
    new_last_day = base_queryset.filter(date__range=[datetime.today() - timedelta(days=1), datetime.today()]).count()
    new_count = base_queryset.filter(status=Grievance.REVIEW).count()
    # TODO Replace below with distinct query in Production server
    no_days = base_queryset.values('date').annotate(date_count=Count('id')).count()
    if no_days:
        avg_per_day = int(round(total_count / no_days))
    else:
        avg_per_day = 0
    pending_count = base_queryset.filter(status=Grievance.PENDING).count()
    pending_inc_count = base_queryset.filter(status=Grievance.PENDING,
                                             date__range=[datetime.today() - timedelta(days=1),
                                                          datetime.today()]).count()
    resolved_count = base_queryset.filter(status=Grievance.RESOLVED).count()
    resolved_inc_count = base_queryset.filter(status=Grievance.RESOLVED,
                                              date__range=[datetime.today() - timedelta(days=1),
                                                           datetime.today()]).count()
    subcategory_select = SelectSubCategoryForm(redressal_body=redressal_body)
    context = {
        'total_count': total_count,
        'new_last_day': new_last_day,
        'new_count': new_count,
        'avg_per_day': avg_per_day,
        'pending_count': pending_count,
        'pending_inc_count': pending_inc_count,
        'resolved_count': resolved_count,
        'resolved_inc_count': resolved_inc_count,
        'subcategory_select': subcategory_select,
    }
    return render(request, 'redressal/view_charts.html', context)


def status_chart_helper(redressal_body, status_filtered):
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
    return data


@is_committee_member(raise_denied=True)
def status_stats_chart(request):
    redressal_body = request.user.get_redressal_body()
    status_filtered = Grievance.objects.filter(redressal_body=redressal_body).exclude(status=Grievance.DRAFT).order_by(
        'status').values('status').annotate(count=Count('id'))
    data = status_chart_helper(redressal_body, status_filtered)
    return JsonResponse(data=data)


@is_committee_member(raise_denied=True)
def status_chart_for_subcategory(request):
    redressal_body = request.user.get_redressal_body()
    subcategory_select = SelectSubCategoryForm(request.GET, redressal_body=redressal_body)
    if subcategory_select.is_valid():
        sub_category = subcategory_select.cleaned_data['sub_category']
    else:
        return HttpResponseNotFound(json.dumps({'detail': 'Not Found'}), content_type="application/json")
    count = Grievance.objects.filter(redressal_body=redressal_body, sub_category=sub_category).exclude(
        status=Grievance.DRAFT).count()
    if not count:
        return HttpResponseNotFound(json.dumps({'detail': 'No data'}), content_type="application/json")
    status_filtered = Grievance.objects.filter(redressal_body=redressal_body, sub_category=sub_category).exclude(
        status=Grievance.DRAFT).order_by(
        'status').values('status').annotate(count=Count('id'))
    data = status_chart_helper(redressal_body, status_filtered)
    return JsonResponse(data=data)


@is_committee_member(raise_denied=True)
def subcategory_stats_chart(request):
    redressal_body = request.user.get_redressal_body()
    subcategory = SubCategory.objects.filter(redressal_body=redressal_body).annotate(grievance_count=Count('grievance'))
    labels = []
    data = []
    for entry in subcategory:
        labels.append(entry.sub_type)
        data.append(entry.grievance_count)
    data = {
        'labels': labels,
        'datasets': [
            {
                'data': data,
            },
        ]
    }
    return JsonResponse(data=data)


@is_committee_member(raise_denied=True)
def grievances_line_chart(request):
    r_body = request.user.get_redressal_body()
    data_t = []
    data_r = []
    # TODO query for production server with distinct clause
    # gr_list = Grievance.objects.annotate(t_count=Window(expression=Count('id'), order_by=F('date').asc()))
    gr_list = Grievance.objects.filter(
        redressal_body=r_body).exclude(status=Grievance.DRAFT).order_by('date').values('date').annotate(
        t_count=Count('id'))
    gr_list_2 = Grievance.objects.filter(
        redressal_body=r_body, status=Grievance.RESOLVED).exclude(status=Grievance.DRAFT).order_by(
        'last_update').values('last_update').annotate(
        r_count=Count('id'))
    for entry in gr_list:
        data_t.append({'x': entry['date'], 'y': entry['t_count']})
    if gr_list:
        entry = gr_list[0]
        data_r.append({'x': entry['date'], 'y': 0})
    for entry in gr_list_2:
        data_r.append({'x': entry['last_update'], 'y': entry['r_count']})
    for i in range(1, len(data_t)):
        data_t[i]['y'] += data_t[i - 1]['y']
    for i in range(1, len(data_r)):
        data_r[i]['y'] += data_r[i - 1]['y']
    data = {
        'datasets': [
            {
                'label': 'Total Grievances',
                'data': data_t,
                'borderColor': "#3e95cd",
            },
            {
                'label': 'Resolved Grievances',
                'data': data_r,
                'borderColor': "#8e5ea2",
            }
        ]
    }
    return JsonResponse(data=data)


def rating_bar_chart(request):
    redressal_body = request.user.get_redressal_body()
    rating_values = Rating.objects.filter(grievance__redressal_body=redressal_body).order_by('rating').values('rating').annotate(
        rating_count=Count('id'))
    labels = ['5', '4', '3', '2', '1']
    data = [0 for i in range(5)]
    for rating in rating_values:
        data[5 - rating['rating']] = rating['rating_count']
    data = {
        'labels': labels,
        'datasets': [{
            'label': 'Ratings',
            'data': data,
            'backgroundColor': [
                '#9cc168',
                '#a9d652',
                '#fdd44d',
                '#fcb556',
                '#f78961',
            ],
            'borderWidth': 1
        }]
    }
    return JsonResponse(data=data)
