from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound, Http404

from .models import Grievance

from functools import wraps


def is_owner_of_grievance(function=None, raise_denied=False):
    def real_wrapper(function, raise_denied=False):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            token = kwargs['token']
            grievance = Grievance.get_from_token(token)
            if not grievance:
                raise Http404()
            if request.user.is_authenticated and grievance.user == request.user:
                return function(request, *args, **kwargs)
            if raise_denied:
                raise PermissionDenied
            raise Http404()
        return wrapper
    if function:
        return real_wrapper(function, raise_denied=raise_denied)
    return real_wrapper
