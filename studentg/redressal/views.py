from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.forms import inlineformset_factory
from .forms import NewRedressalBodyForm
from .models import Redressal_Body,University,Institute,Department
from accounts.forms import NewTempUserForm
from accounts.models import Temp_User, User
from django.http import HttpResponseNotFound, Http404

# Create your views here.


def add_uni(request):
    if request.user.is_superuser ==False:
        raise Http404()
    if request.method == 'POST':
        rbody_form = NewRedressalBodyForm(request.POST)
        tuser_form = NewTempUserForm(request.POST)
        if rbody_form.is_valid() and tuser_form.is_valid():
            rbody = rbody_form.save()
            university=University()
            university.redressal_body=rbody
            university.save()
            temp_user=tuser_form.save(commit=False)
            temp_user.redressal_body=rbody
            temp_user.designation="University_H"
            temp_user.save()
            return redirect('home')
    else:
        rbody_form = NewRedressalBodyForm()
        tuser_form = NewTempUserForm()
    return render(request, 'adduni.html', {'rbody_form': rbody_form, 'tuser_form': tuser_form})
