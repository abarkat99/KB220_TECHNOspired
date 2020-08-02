from .models import RedressalBody
from accounts.models import User


def get_redressal_body_members(redressal_body):
    if redressal_body.body_type == RedressalBody.UNIVERSITY:
        return User.objects.filter(universitymember__in=redressal_body.universitymember_set.all())
    elif redressal_body.body_type == RedressalBody.INSTITUTE:
        return User.objects.filter(institutemember__in=redressal_body.institutemember_set.all())
    elif redressal_body.body_type == RedressalBody.DEPARTMENT:
        return User.objects.filter(departmentmember__in=redressal_body.departmentmember_set.all())