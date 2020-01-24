from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.forms import inlineformset_factory
from .forms import NewRedressalBodyForm, NewSubCategoryForm
from .models import Redressal_Body, University, Institute, Department, Sub_Category
from accounts.forms import NewTempUserForm
from accounts.models import Temp_User, User, University_Member, Institute_Member, Department_Member
from django.http import HttpResponseNotFound, Http404
from django.core.mail import send_mail
from django.urls import reverse
from django import forms
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from functools import wraps
import datetime

from studentg.models import Grievance,Reply
from studentg.forms import GrievanceUpdateForm,NewReplyForm

# One Time Link
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.crypto import salted_hmac
import six
import random
from django.utils import timezone
# Create your views here.


def add_body(request, body_type):
    if request.user.is_superuser != True:
        if request.user.sys_user.designation != "University_H" and request.user.sys_user.designation != "Institute_H":
            raise Http404()
    elif request.user.is_superuser == True and body_type != "university":
        raise Http404()
    elif request.user.is_superuser != True:
        if request.user.sys_user.designation == "University_H" and body_type != "institute":
            raise Http404()
        elif request.user.sys_user.designation == "Institute_H" and body_type != "department":
            raise Http404()
    if request.method == 'POST':
        rbody_form = NewRedressalBodyForm(request.POST)
        tuser_form = NewTempUserForm(request.POST)
        if rbody_form.is_valid() and tuser_form.is_valid():
            rbody = rbody_form.save()
            body_object = None
            if body_type == "university":
                body_object = University()
            elif body_type == "institute":
                body_object = Institute()
                body_object.university = University_Member.objects.get(
                    user=request.user.pk).university
            elif body_type == "department":
                body_object = Department()
                body_object.institute = Institute_Member.objects.get(
                    user=request.user.pk).institute
            body_object.redressal_body = rbody
            body_object.save()
            temp_user = tuser_form.save(commit=False)
            temp_user.redressal_body = rbody
            if body_type == "university":
                temp_user.designation = "University_H"
            elif body_type == "institute":
                temp_user.designation = "Institute_H"
            elif body_type == "department":
                temp_user.designation = "Department_H"
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
            sub_cat = Sub_Category()
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


def add_subcategory(request):
    if request.method == 'POST':
        form = NewSubCategoryForm(request.POST)
        if form.is_valid():
            subcat = form.save(commit=False)
            if request.user.sys_user.designation == "University_H":
                subcat.redressal_body = University_Member.objects.get(
                    user=request.user).university.redressal_body
            elif request.user.sys_user.designation == "Institute_H":
                subcat.redressal_body = Institute_Member.objects.get(
                    user=request.user).institute.redressal_body
            elif request.user.sys_user.designation == "Department_H":
                subcat.redressal_body = Department_Member.objects.get(
                    user=request.user).department.redressal_body
            subcat.save()
            return redirect('dash_home')
    else:
        form = NewSubCategoryForm()
    return render(request, 'add_subcategory.html', {'form': form})


def view_grievances(request):
    r_body = None
    if request.user.sys_user.designation == "University" or request.user.sys_user.designation == "University_H":
        r_body = University_Member.objects.get(
            user=request.user).university.redressal_body
    elif request.user.sys_user.designation == "Institute" or request.user.sys_user.designation == "Institute_H":
        r_body = Institute_Member.objects.get(
            user=request.user).institute.redressal_body
    elif request.user.sys_user.designation == "Department" or request.user.sys_user.designation == "Department_H":
        r_body = Department_Member.objects.get(
            user=request.user).department.redressal_body
    else:
        raise Http404()
    gr_list = Grievance.objects.filter(
        redressal_body=r_body, status="Pending").order_by('last_update')
    return render(request, 'view_grievances.html', {'gr_list': gr_list})

def update_grievance(request, token):
    if request.user.is_superuser:
        raise Http404()
        designation = request.user.sys_user.designation
        if designation == 'Student':
            raise Http404()
        date=datetime.datetime.strptime(token[:-4], "%Y%m%d").date()
        daytoken=int(token[-4:])
        grievance=get_object_or_404(Grievance,date=date,daytoken=daytoken)
        if (designation == "University" or designation == "University_H") and grievance.category=="University":
            if(grievance.redressal_body!=University_Member.objects.get(user=request.user).university.redressal_body):
                raise Http404()
        elif (designation == "Institute" or designation == "Institute_H") and grievance.category=="Institute":
            if(grievance.redressal_body!=Institute_Member.objects.get(user=request.user).institute.redressal_body):
                raise Http404()
        elif (designation == "Department" or designation == "Department_H") and grievance.category=="Department":
            if(grievance.redressal_body!=Department_Member.objects.get(user=request.user).department.redressal_body):
                raise Http404()
        else:
            raise Http404()
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
            reply.grievance=grievance
            reply.save()
            return redirect('view_grievances')
    else:
        gr_upform = GrievanceUpdateForm(instance=grievance)
        reply_form=NewReplyForm()
    return render(request, 'update_grievance.html', {'gr_upform': gr_upform, 'reply_form':reply_form,'replies':replies})