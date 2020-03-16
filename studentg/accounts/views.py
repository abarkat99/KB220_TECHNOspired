from django.contrib.auth import login
from django.shortcuts import render, reverse, redirect, get_object_or_404
from .models import TempUser, User, Student, UniversityMember, InstituteMember, DepartmentMember, StudentTempUser
from .forms import SignUpForm
from redressal.models import RedressalBody, University, Institute, Department
from django.utils import timezone
import datetime

# Create your views here.
def signup(request,uidb64,token):
    t_user=get_object_or_404(TempUser, uidb64=uidb64, token=token)
    if (t_user.created_at < timezone.now() - datetime.timedelta(days=1)):
        if(t_user.designation==TempUser.UNI_HEAD or t_user.designation==TempUser.INS_HEAD or t_user.designation==TempUser.DEP_HEAD):
            t_user.redressal_body.delete()
        return render(request, 'link_expired.html')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email=t_user.email
            user.user=user
            user.first_name=t_user.first_name
            user.last_name=t_user.last_name
            user.designation=t_user.designation
            user_obj=None
            if(t_user.designation==TempUser.STUDENT):
                user_obj=Student()
                st_t_user=t_user.studenttempuser
                user_obj.rollno=st_t_user.rollno
            elif(t_user.designation==TempUser.UNIVERSITY or t_user.designation==TempUser.UNI_HEAD):
                user_obj=UniversityMember()
            elif(t_user.designation==TempUser.INSTITUTE or t_user.designation==TempUser.INS_HEAD):
                user_obj=InstituteMember()
            elif(t_user.designation==TempUser.DEPARTMENT or t_user.designation==TempUser.DEP_HEAD):
                user_obj=DepartmentMember()
            user_obj.redressal_body=t_user.redressal_body
            user_obj.user=user
            user.save()
            user_obj.save()
            login(request, user)
            t_user.delete()
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})