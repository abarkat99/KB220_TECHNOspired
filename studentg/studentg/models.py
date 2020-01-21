from django.db import models
from accounts.models import User
from datetime import date as date_fun
from redressal.models import Sub_Category, Redressal_Body

class Grievance(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='grievance')
    date=models.DateField(auto_now_add=True)
    redressal_body=models.ForeignKey(Redressal_Body, on_delete=models.CASCADE, related_name='grievance')

    def increment_daytoken():
        gr_obj=Grievance.objects.all().filter(date__exact=date_fun.today()).order_by('-daytoken')
        if (gr_obj):
            return gr_obj[0].daytoken+1
        return 1
    daytoken=models.IntegerField(default=increment_daytoken)
    
    last_update=models.DateField(auto_now_add=True)
    status=models.CharField(max_length=10, choices=[('Pending', 'Pending'),('Resolved', 'Resolved'),], default='Pending')

    message=models.TextField(max_length=1000)
    subject=models.CharField(max_length=255)
    image=models.ImageField(null=True,blank=True)
    CATEGORY_CHOICES = [
        ('University', 'University'),
        ('Institute', 'Institute'),
        ('Department', 'Department'),
     ]
    category=models.CharField(max_length=15,choices=CATEGORY_CHOICES)
    sub_category=models.ForeignKey(Sub_Category,on_delete=models.CASCADE)
    class Meta:
        unique_together = (("date", "daytoken"),)

class Reply(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    grievance=models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='reply')
    date_time=models.DateTimeField(auto_now_add=True)
    message=models.TextField(max_length=1000)