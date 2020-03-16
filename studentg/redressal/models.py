from django.db import models

# Create your models here.
class RedressalBody(models.Model):
    name=models.CharField(max_length=255)
    UNIVERSITY = 'UNI'
    INSTITUTE = 'INS'
    DEPARTMENT = 'DEP'
    TYPE_CHOICES = [
        ('UNI', 'University'),
        ('INS', 'Institute'),
        ('DEP', 'Department'),
    ]
    body_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    def get_body_object(self):
        if self.body_type==UNIVERSITY:
            return self.university
        elif self.body_type==INSTITUTE:
            return self.institute
        elif self.body_type==DEPARTMENT:
            return self.department

class SubCategory(models.Model):
    sub_type=models.CharField(max_length=255)
    redressal_body=models.ForeignKey(RedressalBody, on_delete=models.CASCADE, related_name='subcategories')
    class Meta:
        unique_together = (("sub_type", "redressal_body"),)
    def __str__(self):
        return self.sub_type
    

class University(models.Model):
    redressal_body=models.OneToOneField(RedressalBody, on_delete=models.CASCADE)

class Institute(models.Model):
    redressal_body=models.OneToOneField(RedressalBody, on_delete=models.CASCADE)
    university=models.ForeignKey(University, on_delete=models.CASCADE)

class Department(models.Model):
    redressal_body=models.OneToOneField(RedressalBody, on_delete=models.CASCADE)
    institute=models.ForeignKey(Institute, on_delete=models.CASCADE)