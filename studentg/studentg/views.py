from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import HttpResponseNotFound, Http404

from accounts.forms import NewTempUserForm, NewStudentForm, NewMassStudentForm
from accounts.models import Student, DepartmentMember, TempUser, StudentTempUser

from redressal.models import SubCategory

import datetime

from .forms import NewGrievanceForm,NewReplyForm
from .models import DayToken,Grievance,Reply

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.crypto import salted_hmac
import six
import random
from django.utils import timezone
import pandas as pd

from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        return redirect('dash_home')
    return render(request, 'home.html')

def faq(request):
    return render(request, 'faq.html')

@login_required
def dash_home(request):
    return render(request, 'dash_home.html')


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
            grievance.daytoken=DayToken.get_new_token()
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
    date=datetime.datetime.strptime(token[:-4], "%stY%m%d").date()
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