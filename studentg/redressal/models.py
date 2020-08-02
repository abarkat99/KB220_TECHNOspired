from django.db import models

from accounts.constants import DesignationConstants, TempDesignationConstants


# Create your models here.


class RedressalBody(models.Model):
    name = models.CharField(max_length=255)
    UNIVERSITY = 'UNI'
    INSTITUTE = 'INS'
    DEPARTMENT = 'DEP'
    TYPE_CHOICES = [
        ('UNI', 'University'),
        ('INS', 'Institute'),
        ('DEP', 'Department'),
    ]
    body_type = models.CharField(max_length=3, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name

    def get_body_object(self):
        if self.body_type == self.UNIVERSITY:
            return self.university
        elif self.body_type == self.INSTITUTE:
            return self.institute
        elif self.body_type == self.DEPARTMENT:
            return self.department

    def get_head(self):
        if self.body_type == self.UNIVERSITY:
            if self.universitymember_set.exists():
                return self.universitymember_set.filter(user__designation=DesignationConstants.UNI_HEAD)[0].user
            return self.tempuser_set.filter(designation=TempDesignationConstants.UNI_HEAD)[0]
        elif self.body_type == self.INSTITUTE:
            if self.institutemember_set.exists():
                return self.institutemember_set.filter(user__designation=DesignationConstants.INS_HEAD)[0].user
            return self.tempuser_set.filter(designation=TempDesignationConstants.INS_HEAD)[0]
        elif self.body_type == self.DEPARTMENT:
            if self.departmentmember_set.exists():
                return self.departmentmember_set.filter(user__designation=DesignationConstants.DEP_HEAD)[0].user
            return self.tempuser_set.filter(designation=TempDesignationConstants.DEP_HEAD)[0]

    class Meta:
        verbose_name_plural = "Redressal Bodies"


class SubCategory(models.Model):
    sub_type = models.CharField(max_length=255)
    LOW = 0
    HIGH = 1
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (HIGH, 'High'),
    ]
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=LOW)
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        unique_together = (("sub_type", "redressal_body"),)
        verbose_name_plural = "Sub categories"

    def __str__(self):
        return self.sub_type


class University(models.Model):
    redressal_body = models.OneToOneField(RedressalBody, on_delete=models.CASCADE)
    IS_SUB_BODY = False

    def get_sub_bodies(self):
        bodies = RedressalBody.objects.filter(institute__in=self.institute_set.all())
        in_bodies = bodies.filter(tempuser__designation=TempDesignationConstants.INS_HEAD)
        bodies = bodies.exclude(tempuser__designation=TempDesignationConstants.INS_HEAD)
        return bodies, in_bodies

    def __str__(self):
        return self.redressal_body.name


class Institute(models.Model):
    redressal_body = models.OneToOneField(RedressalBody, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    IS_SUB_BODY = True

    def get_sub_bodies(self):
        bodies = RedressalBody.objects.filter(department__in=self.department_set.all())
        in_bodies = bodies.filter(tempuser__designation=TempDesignationConstants.DEP_HEAD)
        bodies = bodies.exclude(tempuser__designation=TempDesignationConstants.DEP_HEAD)
        return bodies, in_bodies
    
    def get_super_body(self):
        return self.university.redressal_body

    def __str__(self):
        return self.redressal_body.name

class Department(models.Model):
    redressal_body = models.OneToOneField(RedressalBody, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    IS_SUB_BODY = True

    def get_super_body(self):
        return self.institute.redressal_body

    def __str__(self):
        return self.redressal_body.name
