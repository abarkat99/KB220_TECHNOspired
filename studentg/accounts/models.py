from django.db import models
from django.contrib.auth.models import User
from redressal.models import University, Institute, Department, Redressal_Body
# Create your models here.


class Sys_User(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="sys_user")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    STUDENT = 'ST'
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
        (UNI_HEAD, 'University_H'),
        (INS_HEAD, 'Institute_H'),
        (DEP_HEAD, 'Department_H'),
    ]
    designation = models.CharField(max_length=15, choices=DESIGNATION_CHOICES)
    def get_designation_object(self):
        if self.designation=='Student':
            return Student.objects.get(user=self.user)
        elif self.designation=='University' or self.designation=='University_H':
            return University_Member.objects.get(user=self.user)
        elif self.designation=='Institute' or self.designation=='Institute_H':
            return Institute_Member.objects.get(user=self.user)
        elif self.designation=='Department' or self.designation=='Department_H':
            return Department_Member.objects.get(user=self.user)
    def get_redressal_body(self):
        return self.get_designation_object().get_redressal_body()

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    rollno=models.IntegerField(unique=True)
    class Meta:
        unique_together=(("department", "rollno"),)
        
    def get_redressal_body(self):
        return self.department.redressal_body

class University_Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    def get_redressal_body(self):
        return self.university.redressal_body
    def get_body_members(self):
        return User.objects.filter(university_member__in=self.university.university_member_set.all())

class Institute_Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    def get_redressal_body(self):
        return self.institute.redressal_body
    def get_body_members(self):
        return User.objects.filter(institute_member__in=self.institute.institute_member_set.all())

class Department_Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    def get_redressal_body(self):
        return self.department.redressal_body
    def get_body_members(self):
        return User.objects.filter(department_member__in=self.department.department_member_set.all())

class Temp_User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    email=models.EmailField()
    redressal_body = models.ForeignKey(Redressal_Body, on_delete=models.CASCADE)
    STUDENT = 'ST'
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
        (UNI_HEAD, 'University_H'),
        (INS_HEAD, 'Institute_H'),
        (DEP_HEAD, 'Department_H'),
    ]
    designation = models.CharField(max_length=15, choices=DESIGNATION_CHOICES)
    uidb64=models.CharField(max_length=255)
    token=models.CharField(max_length=255)

class Student_Temp_User(models.Model):
    user = models.ForeignKey(Temp_User, on_delete=models.CASCADE, related_name='student')
    rollno=models.IntegerField()