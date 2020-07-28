from accounts.forms import NewTempUserForm, NewStudentForm, NewMassStudentForm
from accounts.models import TempUser, StudentTempUser, User, UniversityMember, InstituteMember, DepartmentMember, \
    Student

from studentg.models import Grievance, Reply
from studentg.forms import GrievanceUpdateForm, NewReplyForm
from studentg.constants import STATUS_COLOR_CONVERTER, STATUS_DISPLAY_CONVERTER

from .decorators import is_committee_head, is_committee_member, is_committee_head_of_super_body_type, \
    is_committee_member_of_grievance, is_department_member, is_committee_head_of
from .filters import RedressalGrievanceFilter, FilteredListView
from .forms import NewRedressalBodyForm, NewSubCategoryForm
from .models import RedressalBody, University, Institute, Department, SubCategory

from django.views.generic import TemplateView, CreateView, View, FormView
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseNotFound, Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView
import datetime

# One Time Link
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.crypto import salted_hmac
import six
import pandas as pd
import random
from django.utils import timezone

# Charts
from django.db.models import Count


class HomeView(LoginView):
    template_name = 'redressal/home.html'


class DashboardView(TemplateView):
    template_name = 'redressal/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        redressal_body = self.request.user.get_redressal_body()
        grievances = Grievance.objects.filter(redressal_body=redressal_body).exclude(status=Grievance.DRAFT).order_by(
            '-last_update')[:10]
        context['grievances'] = grievances
        return context


class ViewSubcategories(CreateView):
    model = SubCategory
    form_class = NewSubCategoryForm
    template_name = "redressal/view_subcategories.html"
    success_url = reverse_lazy("view/subcategories/")

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


class SetGrievanceStatus(View):
    status_to_set = None

    def get(self, request, token, *args, **kwargs):
        grievance = Grievance.get_from_token(token)
        if not grievance:
            raise Http404()
        grievance.status = self.status_to_set
        grievance.save()
        return redirect(self.request.META.get('HTTP_REFERER', 'dashboard'))


class SetGrievancePending(SetGrievanceStatus):
    status_to_set = Grievance.PENDING


class SetGrievanceRejected(SetGrievanceStatus):
    status_to_set = Grievance.REJECTED


class SetGrievanceReview(SetGrievanceStatus):
    status_to_set = Grievance.REVIEW


class SetGrievanceResolved(SetGrievanceStatus):
    status_to_set = Grievance.RESOLVED


class ViewGrievanceMessages(TemplateView):
    template_name = 'common/view_messages_modal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grievance = Grievance.get_from_token(kwargs['token'])
        replies = Reply.objects.filter(grievance=grievance)
        allow_reply = True
        context['grievance'] = grievance
        context['replies'] = replies
        context['allow_reply'] = allow_reply
        return context


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


class DeleteInvitedMember(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            TempUser.objects.get(pk=pk).delete()
        except TempUser.MultipleObjectsReturned:
            raise Http404()
        return redirect('view_members')


class DeleteMember(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            User.objects.get(pk=pk).delete()
        except User.MultipleObjectsReturned:
            raise Http404()
        return redirect('view_members')


class ViewBodies(TemplateView):
    template_name = 'redressal/view_bodies.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            bodies = RedressalBody.objects.filter(body_type=RedressalBody.UNIVERSITY)
            in_bodies = bodies.filter(tempuser__designation=User.UNI_HEAD)
            bodies = bodies.exclude(tempuser__designation=User.UNI_HEAD)
        else:
            bodies, in_bodies = self.request.user.get_redressal_body().get_body_object().get_sub_bodies()
        context['bodies'] = bodies
        context['in_bodies'] = in_bodies
        return context


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


class DeleteBody(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            RedressalBody.objects.get(pk=pk).delete()
        except User.MultipleObjectsReturned:
            raise Http404()
        return redirect('view_bodies')


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


class AddStudent(FormView):
    template_name = 'redressal/add_student.html'
    form_class = NewMassStudentForm
    success_url = reverse_lazy('view_students')

    def form_valid(self, form):
        excel_file = self.request.FILES['file']
        data = pd.read_csv(excel_file)
        df = pd.DataFrame(
            data, columns=['Fname', 'Lname', 'Email', 'Rollno'])
        for index, row in df.iterrows():
            tuser = TempUser()
            tuser.first_name = row['Fname']
            tuser.last_name = row['Lname']
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


# # Create your views here.
# @is_committee_head_of_super_body_type(raise_denied=True)
# def add_body(request, body_type):
#     if request.method == 'POST':
#         rbody_form = NewRedressalBodyForm(request.POST)
#         tuser_form = NewTempUserForm(request.POST)
#         if rbody_form.is_valid() and tuser_form.is_valid():
#             rbody = rbody_form.save(commit=False)
#             body_object = None
#             if body_type == "university":
#                 rbody.body_type = RedressalBody.UNIVERSITY
#                 body_object = University()
#             elif body_type == "institute":
#                 rbody.body_type = RedressalBody.INSTITUTE
#                 body_object = Institute()
#                 body_object.university = request.user.universitymember.redressal_body.university
#             elif body_type == "department":
#                 rbody.body_type = RedressalBody.DEPARTMENT
#                 body_object = Department()
#                 body_object.institute = request.user.institutemember.redressal_body.institute
#             rbody.save()
#             body_object.redressal_body = rbody
#             body_object.save()
#             temp_user = tuser_form.save(commit=False)
#             temp_user.redressal_body = rbody
#             if body_type == "university":
#                 temp_user.designation = TempUser.UNI_HEAD
#             elif body_type == "institute":
#                 temp_user.designation = TempUser.INS_HEAD
#             elif body_type == "department":
#                 temp_user.designation = TempUser.DEP_HEAD
#             temp_user.created_at = timezone.now()
#             temp_user.uidb64 = urlsafe_base64_encode(force_bytes(
#                 six.text_type(temp_user.pk) + six.text_type(temp_user.created_at))[::3])
#             value = six.text_type(temp_user.email) + six.text_type(temp_user.designation) + \
#                     six.text_type(temp_user.first_name) + \
#                     six.text_type(temp_user.last_name) + \
#                     six.text_type(temp_user.created_at)
#             temp_user.token = salted_hmac(
#                 "%s" % (random.random()), value).hexdigest()[::3]
#             temp_user.save()
#             sub_cat = SubCategory()
#             sub_cat.sub_type = "Other"
#             sub_cat.redressal_body = rbody
#             sub_cat.save()
#             send_mail(
#                 'Sign Up for Student Grievance Portal',
#                 'Click this link to sign up %s' % (reverse('signup', kwargs={
#                     'uidb64': temp_user.uidb64,
#                     'token': temp_user.token
#                 })),
#                 'from@example.com',
#                 [temp_user.email],
#                 fail_silently=False,
#             )
#             return redirect('dash_home')
#     else:
#         rbody_form = NewRedressalBodyForm()
#         tuser_form = NewTempUserForm()
#     return render(request, 'addbody.html', {'rbody_form': rbody_form, 'tuser_form': tuser_form, 'body_type': body_type})
#
#
# @is_committee_head(raise_denied=True)
# def manage_members(request):
#     if request.method == 'POST':
#         form = NewTempUserForm(request.POST)
#         if form.is_valid():
#             temp_user = form.save(commit=False)
#             temp_user.redressal_body = request.user.get_redressal_body()
#             temp_user.designation = request.user.designation[:-2]
#             temp_user.created_at = timezone.now()
#             temp_user.uidb64 = urlsafe_base64_encode(force_bytes(
#                 six.text_type(temp_user.pk) + six.text_type(temp_user.created_at))[::3])
#             value = six.text_type(temp_user.email) + six.text_type(temp_user.designation) + six.text_type(
#                 temp_user.first_name) + six.text_type(temp_user.last_name) + six.text_type(temp_user.created_at)
#             temp_user.token = salted_hmac(
#                 "%s" % (random.random()), value).hexdigest()[::3]
#             temp_user.save()
#             send_mail(
#                 'Sign Up for Student Grievance Portal',
#                 'Click this link to sign up %s' % (reverse('signup', kwargs={
#                     'uidb64': temp_user.uidb64,
#                     'token': temp_user.token
#                 })),
#                 'from@example.com',
#                 [temp_user.email],
#                 fail_silently=False,
#             )
#     else:
#         form = NewTempUserForm()
#     members = request.user.get_designation_object().get_body_members()
#     in_members = TempUser.objects.filter(redressal_body=request.user.get_redressal_body())
#     return render(request, 'manage_members.html', {'form': form, 'members': members, 'in_members': in_members})
#
#
# @is_committee_head_of(raise_denied=True)
# def remove_member(request, pk):
#     user = get_object_or_404(User, pk=pk)
#     user.delete()
#     return redirect('manage_members')
#
#
# @is_committee_head(raise_denied=True)
# def add_subcategory(request):
#     if request.method == 'POST':
#         form = NewSubCategoryForm(request.POST)
#         if form.is_valid():
#             subcat = form.save(commit=False)
#             subcat.redressal_body = request.user.get_redressal_body()
#             subcat.save()
#             return redirect('dash_home')
#     else:
#         form = NewSubCategoryForm()
#     subcats = SubCategory.objects.filter(redressal_body=request.user.get_redressal_body())
#     return render(request, 'add_subcategory.html', {'form': form, 'subcats': subcats})
#
#
# @is_department_member(raise_denied=True)
# def add_student(request):
#     if request.method == 'POST':
#         tuser_form = NewTempUserForm(request.POST)
#         student_form = NewStudentForm(request.POST)
#         mass_student_form = NewMassStudentForm(request.POST, request.FILES)
#         if mass_student_form.is_valid():
#             excel_file = request.FILES['file']
#             data = pd.read_csv(excel_file)
#             df = pd.DataFrame(
#                 data, columns=['Fname', 'Lname', 'Email', 'Rollno'])
#             for i, j in df.iterrows():
#                 tuser = TempUser()
#                 tuser.first_name = j['Fname']
#                 tuser.last_name = j['Lname']
#                 tuser.email = j['Email']
#                 tuser.created_at = timezone.now()
#                 tuser.redressal_body = request.user.get_redressal_body()
#                 tuser.designation = TempUser.STUDENT
#                 tuser.uidb64 = urlsafe_base64_encode(force_bytes(
#                     six.text_type(tuser.pk) + six.text_type(tuser.created_at))[::3])
#                 value = six.text_type(tuser.email) + six.text_type(tuser.designation) + \
#                         six.text_type(tuser.first_name) + \
#                         six.text_type(tuser.last_name) + \
#                         six.text_type(tuser.created_at)
#                 tuser.token = salted_hmac(
#                     "%s" % (random.random()), value).hexdigest()[::3]
#                 tuser.save()
#                 stuser = StudentTempUser()
#                 stuser.rollno = j['Rollno']
#                 stuser.user = tuser
#                 stuser.save()
#                 send_mail(
#                     'Sign Up for Student Grievance Portal',
#                     'Click this link to sign up %s' % (reverse('signup', kwargs={
#                         'uidb64': tuser.uidb64,
#                         'token': tuser.token
#                     })),
#                     'from@example.com',
#                     [tuser.email],
#                     fail_silently=False,
#                 )
#
#         elif tuser_form.is_valid() and student_form.is_valid():
#             tuser = tuser_form.save(commit=False)
#             tuser.redressal_body = request.user.get_redressal_body()
#             tuser.designation = TempUser.STUDENT
#             tuser.created_at = timezone.now()
#             tuser.uidb64 = urlsafe_base64_encode(force_bytes(
#                 six.text_type(tuser.pk) + six.text_type(tuser.created_at))[::3])
#             value = six.text_type(tuser.email) + six.text_type(tuser.designation) + \
#                     six.text_type(tuser.first_name) + \
#                     six.text_type(tuser.last_name) + \
#                     six.text_type(tuser.created_at)
#             tuser.token = salted_hmac(
#                 "%s" % (random.random()), value).hexdigest()[::3]
#             tuser.save()
#             student = student_form.save(commit=False)
#             student.user = tuser
#             student.save()
#             send_mail(
#                 'Sign Up for Student Grievance Portal',
#                 'Click this link to sign up %s' % (reverse('signup', kwargs={
#                     'uidb64': tuser.uidb64,
#                     'token': tuser.token
#                 })),
#                 'from@example.com',
#                 [tuser.email],
#                 fail_silently=False,
#             )
#     else:
#         tuser_form = NewTempUserForm()
#         student_form = NewStudentForm()
#         mass_student_form = NewMassStudentForm(request.POST)
#     return render(request, 'addstudent.html',
#                   {'tuser_form': tuser_form, 'student_form': student_form, 'mass_student_form': mass_student_form})
#
#
# @is_committee_member(raise_denied=True)
# def view_grievances(request):
#     r_body = request.user.get_redressal_body()
#     gr_list = Grievance.objects.filter(
#         redressal_body=r_body, status="Pending").order_by('last_update')
#     gr_filter = RedressalGrievanceFilter(request.GET, queryset=gr_list, request=request)
#     gr_list = gr_filter.qs
#     page = request.GET.get('page', 1)
#     paginator = Paginator(gr_list, 10)
#     try:
#         gr_list = paginator.page(page)
#     except PageNotAnInteger:
#         gr_list = paginator.page(1)
#     except EmptyPage:
#         gr_list = paginator.page(paginator.num_pages)
#     return render(request, 'view_grievances.html', {'gr_list': gr_list, 'paginator': paginator, 'filter': gr_filter})
#
#
# @is_committee_member_of_grievance(raise_denied=True)
# def update_grievance(request, token):
#     if request.user.is_superuser:
#         raise Http404()
#     designation = request.user.designation
#     if designation == User.STUDENT:
#         raise Http404()
#     date = datetime.datetime.strptime(token[:-4], "%Y%m%d").date()
#     daytoken = int(token[-4:])
#     grievance = get_object_or_404(Grievance, date=date, daytoken=daytoken)
#     if (grievance.redressal_body != request.user.get_redressal_body()):
#         raise Http404
#     date = datetime.datetime.strptime(token[:-4], "%Y%m%d").date()
#     daytoken = int(token[-4:])
#     grievance = get_object_or_404(Grievance, date=date, daytoken=daytoken, status="Pending")
#     replies = Reply.objects.filter(grievance=grievance).order_by('date_time')
#     if request.method == 'POST':
#         gr_upform = GrievanceUpdateForm(request.POST, instance=grievance)
#         reply_form = NewReplyForm(request.POST)
#         if (gr_upform.is_valid() and reply_form.is_valid()):
#             grievance = gr_upform.save()
#             reply = reply_form.save(commit=False)
#             reply.user = request.user
#             reply.save()
#             return redirect('view_grievances')
#     else:
#         gr_upform = GrievanceUpdateForm(instance=grievance)
#         reply_form = NewReplyForm(initial={'grievance': grievance})
#     return render(request, 'update_grievance.html',
#                   {'gr_upform': gr_upform, 'reply_form': reply_form, 'replies': replies})


@is_committee_member(raise_denied=True)
def charts(request):
    return render(request, 'charts.html')


def status_stats_chart(request):
    redressal_body = request.user.get_redressal_body()
    status_filtered = Grievance.objects.filter(redressal_body=redressal_body).exclude(status=Grievance.DRAFT).order_by(
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


@is_committee_member(raise_denied=True)
def grievances_line_chart(request):
    r_body = request.user.get_redressal_body()
    data_t = []
    data_r = []
    # gr_list = Grievance.objects.annotate(t_count=Window(expression=Count('id'), order_by=F('date').asc()))
    gr_list = Grievance.objects.filter(
        redressal_body=r_body).order_by('date').values('date').annotate(t_count=Count('id'))
    gr_list_2 = Grievance.objects.filter(
        redressal_body=r_body, status='Resolved').order_by('last_update').values('last_update').annotate(
        r_count=Count('id'))
    for entry in gr_list:
        data_t.append({'x': entry['date'], 'y': entry['t_count']})
    for entry in gr_list_2:
        data_r.append({'x': entry['last_update'], 'y': entry['r_count']})
    for idx, val in enumerate(data_t):
        val['y'] += data_t[idx - 1]['y']
    for idx, val in enumerate(data_r):
        val['y'] += data_r[idx - 1]['y']
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
