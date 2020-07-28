from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class HostsBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_or_none = super(HostsBackend, self).authenticate(request, username, password, **kwargs)
        if user_or_none:
            if user_or_none.is_superuser and request.host.name == 'admin':
                user_or_none = user_or_none
            elif user_or_none.is_superuser and request.host.name != 'admin':
                user_or_none = None
            elif user_or_none.designation != user_or_none.STUDENT and request.host.name != 'redressal':
                user_or_none = None
            elif user_or_none.designation == user_or_none.STUDENT and request.host.name in ['admin', 'redressal']:
                user_or_none = None
        return user_or_none
