from django.db import models
from django.contrib.auth.models import AbstractUser
from redressal.models import University, Institute, Department, RedressalBody
# Create your models here.

class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    ADMIN = 'ADM'
    STUDENT = 'STU'
    UNIVERSITY = 'UNI'
    INSTITUTE = 'INS'
    DEPARTMENT = 'DEP'
    UNI_HEAD = 'UNI_H'
    INS_HEAD = 'INS_H'
    DEP_HEAD = 'DEP_H'
    DESIGNATION_CHOICES = [
        (ADMIN, 'Admin'),
        (STUDENT, 'Student'),
        (UNIVERSITY, 'University'),
        (INSTITUTE, 'Institute'),
        (DEPARTMENT, 'Department'),
        (UNI_HEAD, 'University Head'),
        (INS_HEAD, 'Institute Head'),
        (DEP_HEAD, 'Department Head'),
    ]
    designation = models.CharField(max_length=5, choices=DESIGNATION_CHOICES)
    REQUIRED_FIELDS = ['first_name','last_name']
    def get_designation_object(self):
        if self.designation==self.STUDENT:
            return self.student
        elif self.designation==self.UNIVERSITY or self.designation==self.UNI_HEAD:
            return self.universitymember
        elif self.designation==self.INSTITUTE or self.designation==self.INS_HEAD:
            return self.institutemember
        elif self.designation==self.DEPARTMENT or self.designation==self.DEP_HEAD:
            return self.departmentmember
    def get_redressal_body(self):
        return self.get_designation_object().redressal_body

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE)
    rollno=models.IntegerField(unique=True)
    class Meta:
        unique_together=(("redressal_body", "rollno"),)
#
class UniversityMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE)
    def get_body_members(self):
        return User.objects.filter(universitymember__in=self.redressal_body.universitymember_set.all())

class InstituteMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE)
    def get_body_members(self):
        return User.objects.filter(institutemember__in=self.redressal_body.institutemember_set.all())

class DepartmentMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE)
    def get_body_members(self):
        return User.objects.filter(departmentmember__in=self.redressal_body.departmentmember_set.all())

class TempUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    email=models.EmailField()
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE)
    STUDENT = 'STU'
    UNIVERSITY = 'UNI'
    INSTITUTE = 'INS'
    DEPARTMENT = 'DEP'
    UNI_HEAD = 'UNI_H'
    INS_HEAD = 'INS_H'
    DEP_HEAD = 'DEP_H'
    DESIGNATION_CHOICES = [
        (STUDENT, 'Student'),
        (UNIVERSITY, 'University'),
        (INSTITUTE, 'Institute'),
        (DEPARTMENT, 'Department'),
        (UNI_HEAD, 'University Head'),
        (INS_HEAD, 'Institute Head'),
        (DEP_HEAD, 'Department Head'),
    ]
    designation = models.CharField(max_length=5, choices=DESIGNATION_CHOICES)
    uidb64=models.CharField(max_length=255)
    token=models.CharField(max_length=255)

class StudentTempUser(models.Model):
    user = models.OneToOneField(TempUser, on_delete=models.CASCADE)
    rollno=models.IntegerField()