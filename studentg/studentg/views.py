from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import HttpResponseNotFound, Http404

from accounts.forms import NewTempUserForm, NewStudentForm
from accounts.models import Student, Department_Member

from redressal.models import Sub_Category

from .forms import NewGrievanceForm
from .models import Grievance

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.crypto import salted_hmac
import six
import random
from django.utils import timezone

from django.core.mail import send_mail


def home(request):
    if request.user.is_authenticated:
        return redirect('dash_home')
    return render(request, 'home.html')


def dash_home(request):
    return render(request, 'dash_home.html')


def add_student(request):
    if request.method == 'POST':
        tuser_form = NewTempUserForm(request.POST)
        student_form = NewStudentForm(request.POST)
        if tuser_form.is_valid() and student_form.is_valid():
            tuser = tuser_form.save(commit=False)
            tuser.redressal_body = Department_Member.objects.get(
                user=request.user.pk).department.redressal_body
            tuser.designation = "Student"
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
    return render(request, 'addstudent.html', {'tuser_form': tuser_form, 'student_form': student_form})


def addgrievance(request):
    if request.method == 'POST':
        form = NewGrievanceForm(request.POST)
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.user = request.user
            r_body = Student.objects.get(user=request.user).department
            if(grievance.category == "University"):
                r_body = r_body.institute.university.redressal_body
            elif(grievance.category == "Institute"):
                r_body = r_body.institute.redressal_body
            elif(grievance.category == "Department"):
                r_body = r_body.redressal_body
            grievance.redressal_body=r_body
        grievance.save()
        return redirect('my_grievances')
    else:
        form = NewGrievanceForm()
    return render(request, 'addgrievance.html', {'form': form})


def load_subcategories(request):
    category = request.GET.get('category')
    print(category)
    st_dept = Student.objects.get(user=request.user).department
    r_body = st_dept
    if(category == "University"):
        r_body = r_body.institute.university.redressal_body
    elif(category == "Institute"):
        r_body = r_body.institute.redressal_body
    elif(category == "Department"):
        r_body = r_body.redressal_body
    subcats = Sub_Category.objects.filter(
        redressal_body=r_body).order_by('sub_type')
    return render(request, 'subcat_options.html', {'subcats': subcats})


def my_grievances(request):
    grievance_list = Grievance.objects.filter(
        user=request.user).order_by('-last_update')
    return render(request, 'my_grievances.html', {'grievance_list': grievance_list})
