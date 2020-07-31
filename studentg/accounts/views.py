from django.contrib.auth import login
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View
from .forms import SignUpForm
from .models import TempUser, User, Student, UniversityMember, InstituteMember, DepartmentMember, StudentTempUser
from redressal.models import RedressalBody, University, Institute, Department
from django.utils import timezone
import datetime


# Create your views here.
class SignupView(View):
    template_name = None

    def get(self, request, *args, **kwargs):
        form = SignUpForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = self.temp_user.email
            user.first_name = self.temp_user.first_name
            user.last_name = self.temp_user.last_name
            user.designation = self.temp_user.designation
            user_obj = None
            if self.temp_user.designation == TempUser.STUDENT:
                user_obj = Student()
                st_t_user = self.temp_user.studenttempuser
                user_obj.rollno = st_t_user.rollno
            elif self.temp_user.designation == TempUser.UNIVERSITY or self.temp_user.designation == TempUser.UNI_HEAD:
                user_obj = UniversityMember()
            elif self.temp_user.designation == TempUser.INSTITUTE or self.temp_user.designation == TempUser.INS_HEAD:
                user_obj = InstituteMember()
            elif self.temp_user.designation == TempUser.DEPARTMENT or self.temp_user.designation == TempUser.DEP_HEAD:
                user_obj = DepartmentMember()
            user_obj.redressal_body = self.temp_user.redressal_body
            user_obj.user = user
            user.save()
            user_obj.save()
            login(request, user)
            self.temp_user.delete()
            return redirect('home')
        print('failed here')
        return render(request, self.template_name, {'form': form})

    def dispatch(self, request, *args, **kwargs):
        self.temp_user = get_object_or_404(TempUser, uidb64=kwargs['uidb64'], token=kwargs['token'])
        if self.temp_user.created_at < timezone.now() - datetime.timedelta(days=1):
            if self.temp_user.designation == TempUser.UNI_HEAD or self.temp_user.designation == TempUser.INS_HEAD or self.temp_user.designation == TempUser.DEP_HEAD:
                self.temp_user.redressal_body.delete()
            return render(request, 'link_expired.html')
        return super(SignupView, self).dispatch(request, *args, **kwargs)
