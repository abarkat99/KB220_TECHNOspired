from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound, Http404

from accounts.models import User, TempUser
from studentg.models import Grievance
from redressal.models import RedressalBody

from functools import wraps
import datetime

# Utility functions here:
def _is_committee_staff(user):
    return (user.designation == User.UNIVERSITY or user.designation == User.INSTITUTE or user.designation == User.DEPARTMENT)

def _is_committee_head(user):
    return (user.designation == User.UNI_HEAD or user.designation == User.INS_HEAD or user.designation == User.DEP_HEAD)

def _is_committee_member(user):
    return _is_committee_staff(user) or _is_committee_head(user)

def _is_department_member(user):
    return user.designation == User.DEPARTMENT or user.designation == User.DEP_HEAD

def _is_committee_head_of_super_body_type(user):
    return user.is_superuser or user.designation == User.UNI_HEAD or user.designation == User.INS_HEAD

def _is_committee_head_of_super_body(user, sub_body):
    return sub_body.IS_SUB_BODY and user.get_redressal_body() == sub_body.get_super_body()

def _is_committee_head_of(user, staff):
    return (staff.get_redressal_body() == user.get_redressal_body()) and _is_committee_head(user)

def _has_rbody_same_as_grievance(user, grievance):
    return user.get_redressal_body() == grievance.redressal_body


# Decorators start here:-
def is_committee_head(function=None, raise_denied=False):
    def real_wrapper(function, raise_denied=False):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and _is_committee_head(request.user):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    if function:
        return real_wrapper(function, raise_denied=raise_denied)
    return real_wrapper

def is_committee_member(function=None, raise_denied=False):
    def real_wrapper(function, raise_denied=False):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and _is_committee_member(request.user):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    if function:
        return real_wrapper(function, raise_denied=raise_denied)
    return real_wrapper

def is_department_member(function=None, raise_denied=False):
    def real_wrapper(function, raise_denied=False):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and _is_department_member(request.user):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    if function:
        return real_wrapper(function, raise_denied=raise_denied)
    return real_wrapper

def is_committee_head_of_super_body_type(function=None, raise_denied=False):
    def real_wrapper(function, raise_denied=False):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and _is_committee_head_of_super_body_type(request.user):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    if function:
        return real_wrapper(function, raise_denied=raise_denied)
    return real_wrapper

def is_committee_head_of_super_body(function=None, raise_denied=False):
    def real_wrapper(function, raise_denied=False):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            sub_body = get_object_or_404(RedressalBody, pk=kwargs['pk']).get_body_object()
            if request.user.is_authenticated and _is_committee_head_of_super_body(request.user, sub_body):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    if function:
        return real_wrapper(function, raise_denied=raise_denied)
    return real_wrapper

def is_committee_head_of_temp_user(function=None, raise_denied=False):
    def real_wrapper(function, raise_denied=False):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            staff = get_object_or_404(TempUser, pk=kwargs['pk'])
            if request.user.is_authenticated and _is_committee_head_of(request.user, staff):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    if function:
        return real_wrapper(function, raise_denied=raise_denied)
    return real_wrapper

def is_committee_head_of(function=None, raise_denied=False):
    def real_wrapper(function, raise_denied=False):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            staff = get_object_or_404(User, pk=kwargs['pk'])
            if request.user.is_authenticated and _is_committee_head_of(request.user, staff):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    if function:
        return real_wrapper(function, raise_denied=raise_denied)
    return real_wrapper

def is_committee_member_of_grievance(function=None, raise_denied=False):
    def real_wrapper(function, raise_denied=False):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            token = kwargs['token']
            grievance = Grievance.get_from_token(token)
            if not grievance:
                raise Http404()
            if request.user.is_authenticated and _has_rbody_same_as_grievance(request.user, grievance):
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    if function:
        return real_wrapper(function, raise_denied=raise_denied)
    return real_wrapper