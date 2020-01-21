from django.db import models

# Create your models here.
class Redressal_Body(models.Model):
    name=models.CharField(max_length=255)

class Sub_Category(models.Model):
    sub_type=models.CharField(max_length=255)
    redressal_body=models.ForeignKey(Redressal_Body, on_delete=models.CASCADE, related_name='sub_category')
    class Meta:
        unique_together = (("sub_type", "redressal_body"),)
    def __str__(self):
        return self.sub_type
    

class University(models.Model):
    redressal_body=models.ForeignKey(Redressal_Body, on_delete=models.CASCADE)

class Institute(models.Model):
    redressal_body=models.ForeignKey(Redressal_Body, on_delete=models.CASCADE)
    university=models.ForeignKey(University, on_delete=models.CASCADE)

class Department(models.Model):
    redressal_body=models.ForeignKey(Redressal_Body, on_delete=models.CASCADE)
    institute=models.ForeignKey(Institute, on_delete=models.CASCADE)