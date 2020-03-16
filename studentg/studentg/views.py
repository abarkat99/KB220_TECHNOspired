from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import HttpResponseNotFound, Http404

from accounts.forms import NewTempUserForm, NewStudentForm, NewMassStudentForm
from accounts.models import Student, DepartmentMember, TempUser, StudentTempUser

from redressal.models import SubCategory

import datetime

from .forms import NewGrievanceForm,NewReplyForm
from .models import Grievance,Reply

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.crypto import salted_hmac
import six
import random
from django.utils import timezone
import openpyxl
import pandas as pd

from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def home(request):
    if request.user.is_authenticated:
        return redirect('dash_home')
    return render(request, 'home.html')

def faq(request):
    return render(request, 'faq.html')

def dash_home(request):
    return render(request, 'dash_home.html')


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


def addgrievance(request):
    if request.method == 'POST':
        form = NewGrievanceForm(request.POST, request.FILES)
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.user = request.user
            r_body=request.user.get_redressal_body()
            if grievance.category != 'Department':
                r_body=r_body.department.institute.redressal_body
                if grievance.category != 'Institute':
                    r_body=r_body.institute.university.redressal_body
                    if grievance.category != 'University':
                        raise Http404
            grievance.redressal_body = r_body
            grievance.save()
        return redirect('my_grievances')
    else:
        form = NewGrievanceForm()
    return render(request, 'addgrievance.html', {'form': form})


def load_subcategories(request):
    category = request.GET.get('category')
    r_body = request.user.get_redressal_body()
    if(category != "Department"):
        r_body = r_body.department.institute.redressal_body
        if(category != "Institute"):
            r_body = r_body.institute.university.redressal_body
            if(category != "University"):
                raise Http404()
    subcats = SubCategory.objects.filter(
        redressal_body=r_body).order_by('sub_type')
    return render(request, 'subcat_options.html', {'subcats': subcats})


def my_grievances(request):
    grievance_list = Grievance.objects.filter(
        user=request.user).order_by('-last_update')
    page=request.GET.get('page',1)
    paginator=Paginator(grievance_list,10)
    try:
        grievance_list = paginator.page(page)
    except PageNotAnInteger:
        grievance_list = paginator.page(1)
    except EmptyPage:
        grievance_list = paginator.page(paginator.num_pages)
    return render(request, 'my_grievances.html', {'grievance_list': grievance_list,'paginator':paginator})

def getgrievance(request,token):
    date=datetime.datetime.strptime(token[:-4], "%Y%m%d").date()
    daytoken=int(token[-4:])
    grievance = get_object_or_404(Grievance, date=date, daytoken=daytoken)
    replies = Reply.objects.filter(grievance=grievance)
    reply_form=None
    if(request.user!=grievance.user):
        raise Http404()
    if (replies):
        if(request.user != replies.last().user):
            reply_form=NewReplyForm(initial={'grievance': grievance})
    return render(request, 'getgrievance.html', {'grievance': grievance, 'replies': replies,'token': token,'reply_form': reply_form})

def contact(request):
    return render(request,"contact.html")
def about_us(request):
    return render(request,"about_us.html")