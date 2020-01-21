from django.contrib.auth import login
from django.shortcuts import render, reverse, redirect, get_object_or_404
from .models import Temp_User, Sys_User, Student, University_Member, Institute_Member, Department_Member, Student_Temp_User
from .forms import SignUpForm
from redressal.models import Redressal_Body, University, Institute, Department
from django.utils import timezone
import datetime

# Create your views here.
def signup(request,uidb64,token):
    t_user=get_object_or_404(Temp_User, uidb64=uidb64, token=token)
    if (t_user.created_at < timezone.now() - datetime.timedelta(days=1)):
        t_user.delete()
        if(t_user.designation=="University_H" or t_user.designation=="Institute_H" or t_user.designation=="Department_H"):
            Redressal_Body.objects.get(pk=t_user.redressal_body).delete()
        return render(request, 'link_expired.html')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email=t_user.email
            user.save()
            sys_user=Sys_User()
            sys_user.user=user
            sys_user.first_name=t_user.first_name
            sys_user.last_name=t_user.last_name
            sys_user.designation=t_user.designation
            user_obj=None
            if(t_user.designation=="Student"):
                user_obj=Student()
                st_t_user=t_user.student.all()[0]
                user_obj.rollno=st_t_user.rollno
                user_obj.department=Department.objects.get(redressal_body=t_user.redressal_body)
            elif(t_user.designation=="University" or t_user.designation=="University_H"):
                user_obj=University_Member()
                user_obj.university=University.objects.get(redressal_body=t_user.redressal_body)
            elif(t_user.designation=="Institute" or t_user.designation=="Institute_H"):
                user_obj=Institute_Member()
                user_obj.institute=Institute.objects.get(redressal_body=t_user.redressal_body)
            elif(t_user.designation=="Department" or t_user.designation=="Department_H"):
                user_obj=Department_Member()
                user_obj.department=Department.objects.get(redressal_body=t_user.redressal_body)
            user_obj.user=user
            sys_user.save()
            user_obj.save()
            login(request, user)
            t_user.delete()
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})