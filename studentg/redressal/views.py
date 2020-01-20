from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.forms import inlineformset_factory
from .forms import NewRedressalBodyForm
from .models import Redressal_Body, University, Institute, Department
from accounts.forms import NewTempUserForm
from accounts.models import Temp_User, User, University_Member, Institute_Member
from django.http import HttpResponseNotFound, Http404
from django.core.mail import send_mail
from django.urls import reverse
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
            temp_user.uidb64 = urlsafe_base64_encode(force_bytes(temp_user.pk))
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
            return redirect('home')
    else:
        rbody_form = NewRedressalBodyForm()
        tuser_form = NewTempUserForm()
    return render(request, 'adduni.html', {'rbody_form': rbody_form, 'tuser_form': tuser_form, 'body_type': body_type})
