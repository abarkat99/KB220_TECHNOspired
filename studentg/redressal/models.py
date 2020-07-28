from django.db import models


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
                return self.universitymember_set.filter(user__designation="UNI_H")[0].user
            return self.tempuser_set.filter(designation="UNI_H")[0]
        elif self.body_type == self.INSTITUTE:
            if self.institutemember_set.exists():
                return self.institutemember_set.filter(user__designation="INS_H")[0].user
            return self.tempuser_set.filter(designation="INS_H")[0]
        elif self.body_type == self.DEPARTMENT:
            if self.departmentmember_set.exists():
                return self.departmentmember_set.filter(user__designation="DEP_H")[0].user
            return self.tempuser_set.filter(designation="DEP_H")[0]


class SubCategory(models.Model):
    sub_type = models.CharField(max_length=255)
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        unique_together = (("sub_type", "redressal_body"),)

    def __str__(self):
        return self.sub_type


class University(models.Model):
    redressal_body = models.OneToOneField(RedressalBody, on_delete=models.CASCADE)

    def get_sub_bodies(self):
        bodies = RedressalBody.objects.filter(institute__in=self.institute_set.all())
        in_bodies = bodies.filter(tempuser__designation="INS_H")
        bodies = bodies.exclude(tempuser__designation="INS_H")
        return bodies, in_bodies


class Institute(models.Model):
    redressal_body = models.OneToOneField(RedressalBody, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    def get_sub_bodies(self):
        bodies = RedressalBody.objects.filter(department__in=self.department_set.all())
        in_bodies = bodies.filter(tempuser__designation="DEP_H")
        bodies = bodies.exclude(tempuser__designation="DEP_H")
        return bodies, in_bodies


class Department(models.Model):
    redressal_body = models.OneToOneField(RedressalBody, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
