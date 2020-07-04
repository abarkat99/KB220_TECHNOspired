from django.shortcuts import render, reverse, redirect, get_object_or_404
from .decorators import is_committee_head, is_committee_member, is_committee_head_of_super_body_type, is_committee_member_of_grievance, is_department_member, is_committee_head_of
from .filters import GrievanceFilter
from .forms import NewRedressalBodyForm, NewSubCategoryForm
from .models import RedressalBody, University, Institute, Department, SubCategory
from accounts.forms import NewTempUserForm, NewStudentForm, NewMassStudentForm
from accounts.models import TempUser, StudentTempUser, User, UniversityMember, InstituteMember, DepartmentMember
from django.http import HttpResponseNotFound, Http404
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django import forms
import datetime

from studentg.models import Grievance, Reply
from studentg.forms import GrievanceUpdateForm, NewReplyForm

# One Time Link
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.crypto import salted_hmac
import six
import pandas as pd
import random
from django.utils import timezone

# Create your views here.
@is_committee_head_of_super_body_type(raise_denied=True)
def add_body(request, body_type):
    if request.method == 'POST':
        rbody_form = NewRedressalBodyForm(request.POST)
        tuser_form = NewTempUserForm(request.POST)
        if rbody_form.is_valid() and tuser_form.is_valid():
            rbody = rbody_form.save(commit=False)
            body_object = None
            if body_type == "university":
                rbody.body_type=RedressalBody.UNIVERSITY
                body_object = University()
            elif body_type == "institute":
                rbody.body_type=RedressalBody.INSTITUTE
                body_object = Institute()
                body_object.university = request.user.universitymember.redressal_body.university
            elif body_type == "department":
                rbody.body_type=RedressalBody.DEPARTMENT
                body_object = Department()
                body_object.institute = request.user.institutemember.redressal_body.institute
            rbody.save()
            body_object.redressal_body = rbody
            body_object.save()
            temp_user = tuser_form.save(commit=False)
            temp_user.redressal_body = rbody
            if body_type == "university":
                temp_user.designation = TempUser.UNI_HEAD
            elif body_type == "institute":
                temp_user.designation = TempUser.INS_HEAD
            elif body_type == "department":
                temp_user.designation = TempUser.DEP_HEAD
            temp_user.created_at = timezone.now()
            temp_user.uidb64 = urlsafe_base64_encode(force_bytes(
                six.text_type(temp_user.pk)+six.text_type(temp_user.created_at))[::3])
            value = six.text_type(temp_user.email)+six.text_type(temp_user.designation) + \
                six.text_type(temp_user.first_name) + \
                six.text_type(temp_user.last_name) + \
                six.text_type(temp_user.created_at)
            temp_user.token = salted_hmac(
                "%s" % (random.random()), value).hexdigest()[::3]
            temp_user.save()
            sub_cat = SubCategory()
            sub_cat.sub_type = "Other"
            sub_cat.redressal_body = rbody
            sub_cat.save()
            send_mail(
                'Sign Up for Student Grievance Portal',
                'Click this link to sign up %s' % (reverse('signup', kwargs={
                    'uidb64': temp_user.uidb64,
                    'token': temp_user.token
                })),
                'from@example.com',
                [temp_user.email],
                fail_silently=False,
            )
            return redirect('dash_home')
    else:
        rbody_form = NewRedressalBodyForm()
        tuser_form = NewTempUserForm()
    return render(request, 'addbody.html', {'rbody_form': rbody_form, 'tuser_form': tuser_form, 'body_type': body_type})

@is_committee_head(raise_denied=True)
def manage_members(request):
    if request.method == 'POST':
        form = NewTempUserForm(request.POST)
        if form.is_valid():
            temp_user = form.save(commit=False)
            temp_user.redressal_body = request.user.get_redressal_body()
            temp_user.designation=request.user.designation[:-2]
            temp_user.created_at = timezone.now()
            temp_user.uidb64 = urlsafe_base64_encode(force_bytes(
                six.text_type(temp_user.pk)+six.text_type(temp_user.created_at))[::3])
            value = six.text_type(temp_user.email)+six.text_type(temp_user.designation) + \
                six.text_type(temp_user.first_name) + \
                six.text_type(temp_user.last_name) + \
                six.text_type(temp_user.created_at)
            temp_user.token = salted_hmac(
                "%s" % (random.random()), value).hexdigest()[::3]
            temp_user.save()
            send_mail(
                'Sign Up for Student Grievance Portal',
                'Click this link to sign up %s' % (reverse('signup', kwargs={
                    'uidb64': temp_user.uidb64,
                    'token': temp_user.token
                })),
                'from@example.com',
                [temp_user.email],
                fail_silently=False,
            )
    else:
        form = NewTempUserForm()
    members=request.user.get_designation_object().get_body_members()
    in_members=TempUser.objects.filter(redressal_body=request.user.get_redressal_body())
    return render(request, 'manage_members.html',{'form':form,'members':members,'in_members':in_members})

@is_committee_head_of(raise_denied=True)
def remove_member(request, pk):
    user=get_object_or_404(User,pk=pk)
    user.delete()
    return redirect('manage_members')

@is_committee_head(raise_denied=True)
def add_subcategory(request):
    if request.method == 'POST':
        form = NewSubCategoryForm(request.POST)
        if form.is_valid():
            subcat = form.save(commit=False)
            subcat.redressal_body=request.user.get_redressal_body()
            subcat.save()
            return redirect('dash_home')
    else:
        form = NewSubCategoryForm()
    subcats=SubCategory.objects.filter(redressal_body=request.user.get_redressal_body())
    return render(request, 'add_subcategory.html', {'form': form,'subcats':subcats})


@is_department_member(raise_denied=True)
def add_student(request):
    if request.method == 'POST':
        tuser_form = NewTempUserForm(request.POST)
        student_form = NewStudentForm(request.POST)
        mass_student_form = NewMassStudentForm(request.POST,request.FILES)
        if mass_student_form.is_valid():
            excel_file = request.FILES['file']
            data = pd.read_csv(excel_file)
            df = pd.DataFrame(
                data, columns=['Fname', 'Lname', 'Email', 'Rollno'])
            for i, j in df.iterrows():
                tuser = TempUser()
                tuser.first_name = j['Fname']
                tuser.last_name = j['Lname']
                tuser.email = j['Email']
                tuser.created_at = timezone.now()
                tuser.redressal_body = request.user.get_redressal_body()
                tuser.designation = TempUser.STUDENT
                tuser.uidb64 = urlsafe_base64_encode(force_bytes(
                    six.text_type(tuser.pk)+six.text_type(tuser.created_at))[::3])
                value = six.text_type(tuser.email)+six.text_type(tuser.designation) + \
                    six.text_type(tuser.first_name) + \
                    six.text_type(tuser.last_name) + \
                    six.text_type(tuser.created_at)
                tuser.token = salted_hmac(
                    "%s" % (random.random()), value).hexdigest()[::3]
                tuser.save()
                stuser = StudentTempUser()
                stuser.rollno = j['Rollno']
                stuser.user = tuser
                stuser.save()
                send_mail(
                    'Sign Up for Student Grievance Portal',
                    'Click this link to sign up %s' % (reverse('signup', kwargs={
                        'uidb64': tuser.uidb64,
                        'token': tuser.token
                    })),
                    'from@example.com',
                    [tuser.email],
                    fail_silently=False,
                )

        elif tuser_form.is_valid() and student_form.is_valid():
            tuser = tuser_form.save(commit=False)
            tuser.redressal_body = request.user.get_redressal_body()
            tuser.designation = TempUser.STUDENT
            tuser.created_at = timezone.now()
            tuser.uidb64 = urlsafe_base64_encode(force_bytes(
                six.text_type(tuser.pk)+six.text_type(tuser.created_at))[::3])
            value = six.text_type(tuser.email)+six.text_type(tuser.designation) + \
                six.text_type(tuser.first_name) + \
                six.text_type(tuser.last_name) + \
                six.text_type(tuser.created_at)
            tuser.token = salted_hmac(
                "%s" % (random.random()), value).hexdigest()[::3]
            tuser.save()
            student = student_form.save(commit=False)
            student.user = tuser
            student.save()
            send_mail(
                'Sign Up for Student Grievance Portal',
                'Click this link to sign up %s' % (reverse('signup', kwargs={
                    'uidb64': tuser.uidb64,
                    'token': tuser.token
                })),
                'from@example.com',
                [tuser.email],
                fail_silently=False,
            )
    else:
        tuser_form = NewTempUserForm()
        student_form = NewStudentForm()
        mass_student_form = NewMassStudentForm(request.POST)
    return render(request, 'addstudent.html', {'tuser_form': tuser_form, 'student_form': student_form, 'mass_student_form': mass_student_form})


@is_committee_member(raise_denied=True)
def view_grievances(request):
    r_body=request.user.get_redressal_body()
    gr_list = Grievance.objects.filter(
        redressal_body=r_body, status="Pending").order_by('last_update')
    gr_filter=GrievanceFilter(request.GET,queryset=gr_list,request=request)
    gr_list=gr_filter.qs
    page=request.GET.get('page',1)
    paginator=Paginator(gr_list,10)
    try:
        gr_list = paginator.page(page)
    except PageNotAnInteger:
        gr_list = paginator.page(1)
    except EmptyPage:
        gr_list = paginator.page(paginator.num_pages)
    return render(request, 'view_grievances.html', {'gr_list': gr_list,'paginator':paginator, 'filter':gr_filter})

@is_committee_member_of_grievance(raise_denied=True)
def update_grievance(request, token):
    if request.user.is_superuser:
        raise Http404()
    designation = request.user.designation
    if designation == User.STUDENT:
        raise Http404()
    date=datetime.datetime.strptime(token[:-4], "%Y%m%d").date()
    daytoken=int(token[-4:])
    grievance=get_object_or_404(Grievance, date=date, daytoken=daytoken)
    if (grievance.redressal_body != request.user.get_redressal_body()):
        raise Http404
    date=datetime.datetime.strptime(token[:-4], "%Y%m%d").date()
    daytoken=int(token[-4:])
    grievance=get_object_or_404(Grievance, date=date, daytoken=daytoken,status="Pending")
    replies=Reply.objects.filter(grievance=grievance).order_by('date_time')
    if request.method == 'POST':
        gr_upform=GrievanceUpdateForm(request.POST, instance=grievance)
        reply_form=NewReplyForm(request.POST)
        if(gr_upform.is_valid() and reply_form.is_valid()):
            grievance=gr_upform.save()
            reply=reply_form.save(commit=False)
            reply.user=request.user
            reply.save()
            return redirect('view_grievances')
    else:
        gr_upform = GrievanceUpdateForm(instance=grievance)
        reply_form=NewReplyForm(initial={'grievance': grievance})
    return render(request, 'update_grievance.html', {'gr_upform': gr_upform, 'reply_form':reply_form,'replies':replies})