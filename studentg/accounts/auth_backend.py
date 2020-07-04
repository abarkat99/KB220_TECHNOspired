from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

UserModel = get_user_model()

class SiteBackend(ModelBackend):
    def authenticate(self, *args, **kwargs):
        user_or_none = super(SiteBackend, self).authenticate(*args, **kwargs)
        if user_or_none and user_or_none.site != Site.objects.get_current():
            user_or_none = None
        return user_or_none

    def get_user(self, user_id):
        try:
            user = UserModel._default_manager.get(pk=user_id, site=Site.objects.get_current())
        except UserModel.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None