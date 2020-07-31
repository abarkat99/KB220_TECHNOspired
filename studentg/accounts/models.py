import random

import six
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.crypto import salted_hmac
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_hosts.resolvers import reverse

from redressal.models import RedressalBody
from .constants import DesignationConstants, TempDesignationConstants


# Create your models here.


class User(DesignationConstants, AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    designation = models.CharField(max_length=5, choices=DesignationConstants.DESIGNATION_CHOICES)
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_designation_object(self):
        if self.designation == self.STUDENT:
            return self.student
        elif self.designation == self.UNIVERSITY or self.designation == self.UNI_HEAD:
            return self.universitymember
        elif self.designation == self.INSTITUTE or self.designation == self.INS_HEAD:
            return self.institutemember
        elif self.designation == self.DEPARTMENT or self.designation == self.DEP_HEAD:
            return self.departmentmember

    def get_redressal_body(self):
        return self.get_designation_object().redressal_body

    def get_body_dict(self):
        dictionary = {}
        redressal_body = self.get_redressal_body()
        if redressal_body.body_type == redressal_body.DEPARTMENT:
            dictionary['dept'] = redressal_body.name
            redressal_body = redressal_body.department.institute.redressal_body
        if redressal_body.body_type == redressal_body.INSTITUTE:
            dictionary['inst'] = redressal_body.name
            redressal_body = redressal_body.institute.university.redressal_body
        dictionary['uni'] = redressal_body.name
        return dictionary


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE)
    rollno = models.IntegerField()

    # class Meta:
    #     unique_together = (("redressal_body", "rollno"),)


class UniversityMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE)

    def get_body_members(self):
        return User.objects.filter(universitymember__in=self.redressal_body.universitymember_set.all()).exclude(
            pk=self.user.pk)


class InstituteMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE)

    def get_body_members(self):
        return User.objects.filter(institutemember__in=self.redressal_body.institutemember_set.all()).exclude(
            pk=self.user.pk)


class DepartmentMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE)

    def get_body_members(self):
        return User.objects.filter(departmentmember__in=self.redressal_body.departmentmember_set.all()).exclude(
            pk=self.user.pk)


class TempUser(TempDesignationConstants, models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE)

    designation = models.CharField(max_length=5, choices=TempDesignationConstants.DESIGNATION_CHOICES)
    uidb64 = models.CharField(max_length=255)
    token = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def save(self, *args, **kwargs):
        if not self.uidb64:
            self.uidb64 = urlsafe_base64_encode(
                force_bytes(six.text_type(self.pk) + six.text_type(self.created_at))[::3])
        if not self.token:
            value = six.text_type(self.email) + six.text_type(self.designation) + six.text_type(
                self.first_name) + six.text_type(self.last_name) + six.text_type(self.created_at)
            self.token = salted_hmac("%s" % (random.random()), value).hexdigest()[::3]
        super(TempUser, self).save(*args, **kwargs)

    def get_redressal_body(self):
        return self.redressal_body

    def send_mail(self):
        if self.designation == self.STUDENT:
            host = 'www'
        else:
            host = 'redressal'
        signup_relative_url = reverse('signup', host=host, kwargs={
            'uidb64': self.uidb64,
            'token': self.token
        })
        send_mail(
            'Sign Up for Student Grievance Portal',
            f'Click this link to sign up http:{signup_relative_url}',
            'st050100@gmail.com',
            [self.email],
            fail_silently=False,
        )


class StudentTempUser(models.Model):
    user = models.OneToOneField(TempUser, on_delete=models.CASCADE)
    rollno = models.IntegerField()
