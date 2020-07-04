from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound, Http404

from accounts.models import User
from studentg.models import Grievance

from functools import wraps
import datetime

# Utility functions here:
def _is_committee_staff(user):
    return (user.designation == 'UNI' or user.designation == 'INS' or user.designation == 'DEP')

def _is_committee_head(user):
    return (user.designation == 'UNI_H' or user.designation == 'INS_H' or user.designation == 'DEP_H')

def _is_committee_member(user):
    return _is_committee_staff(user) or _is_committee_head(user)

def _is_department_member(user):
    return user.designation == 'DEP' or user.designation == 'DEP_H'

def _is_committee_head_of_super_body_type(user, sub_body):
    return (user.is_superuser and sub_body == "university") or (user.designation == 'UNI_H' and sub_body == "institute") or (user.designation == 'INS_H' and sub_body == "department")

def _is_committee_head_of(user, staff):
    return (staff.get_redressal_body() == user.get_redressal_body()) and _is_committee_head(user)

def _has_rbody_same_as_grievance(user, grievance):
    return user.get_redressal_body() == grievance.redressal_body


# Decorators start here:-
def is_committee_head(raise_denied=False):
    def real_wrapper(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and _is_committee_head(request.user):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    return real_wrapper

def is_committee_member(raise_denied=False):
    def real_wrapper(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and _is_committee_member(request.user):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    return real_wrapper

def is_department_member(raise_denied=False):
    def real_wrapper(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and _is_department_member(request.user):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    return real_wrapper

def is_committee_head_of_super_body_type(raise_denied=False):
    def real_wrapper(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and _is_committee_head_of_super_body_type(request.user, kwargs['body_type']):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    return real_wrapper

def is_committee_head_of(raise_denied=False):
    def real_wrapper(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            staff = get_object_or_404(User, pk=kwargs['pk'])
            if request.user.is_authenticated and _is_committee_head_of(request.user, staff):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    return real_wrapper

def is_committee_member_of_grievance(raise_denied=False):
    def real_wrapper(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            token = kwargs['token']
            date = datetime.datetime.strptime(token[:-4], "%Y%m%d").date()
            daytoken = int(token[-4:])
            grievance = get_object_or_404(Grievance, date=date, daytoken=daytoken)
            if request.user.is_authenticated and _has_rbody_same_as_grievance(request.user, grievance):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    return real_wrapper