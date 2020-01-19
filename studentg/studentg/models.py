from django.db import models
from .accounts.models import User
from datetime import date as date_fun

class Grievance(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='grievance')
    date=models.DateField(auto_now_add=True)

    def increment_daytoken():
        gr_obj=Grievance.objects.all().filter(date__exact=date_fun.today()).order_by('-date')[0]
        if (gr_obj):
            return gr_obj.daytoken+1
        return 1
    daytoken=models.IntegerField(default=increment_daytoken)
    message=models.TextField(max_length=1000)
    subject=models.CharField(max_length=255)
    image=models.ImageField(null=True)
    UNIVERSITY = 'UNI'
    INSTITUTE = 'INS'
    DEPARTMENT = 'DEP'
    CATEGORY_CHOICES = [
        (UNIVERSITY, 'University'),
        (INSTITUTE, 'Institute'),
        (DEPARTMENT, 'Department'),
     ]
    category=models.CharField(max_length=15,choices=CATEGORY_CHOICES)
    sub_category=models.CharField(max_length=255,choices=[('OTHER','Other')])
    class Meta:
        unique_together = (("date", "daytoken"),)

class Reply(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    grievance=models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='reply')
    date_time=models.DateTimeField(auto_now_add=True)
    message=models.TextField(max_length=1000)