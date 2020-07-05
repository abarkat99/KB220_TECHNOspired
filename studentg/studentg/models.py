from django.db import models
from django.db import transaction
from accounts.models import User
from datetime import date as date_fun
from redressal.models import SubCategory, RedressalBody

#Concurrency controlled generation of tokens Singleton table
class DayToken(models.Model):
    counter=models.IntegerField(default=0)
    last_update=models.DateField(auto_now_add=True)
    @classmethod
    def get_new_token(cls):
        with transaction.atomic():
            daytoken=cls.objects.select_for_update().first()
            if daytoken==None:
                daytoken=cls()
            if daytoken.last_update!=date_fun.today():
                daytoken.last_update=date_fun.today()
                daytoken.counter=0
            daytoken.counter=daytoken.counter+1
            daytoken.save()
            return daytoken.counter
    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(DayToken, self).save(*args, **kwargs)

class Grievance(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='grievances')
    date=models.DateField(auto_now_add=True)
    redressal_body=models.ForeignKey(RedressalBody, on_delete=models.CASCADE, related_name='grievances')
    daytoken=models.IntegerField()
    
    last_update=models.DateField(auto_now=True)
    status=models.CharField(max_length=10, choices=[('Pending', 'Pending'),('Resolved', 'Resolved'),], default='Pending')

    message=models.TextField(max_length=1000)
    subject=models.CharField(max_length=255)
    image=models.ImageField(null=True,blank=True,upload_to='images/')
    CATEGORY_CHOICES = [
        ('University', 'University'),
        ('Institute', 'Institute'),
        ('Department', 'Department'),
     ]
    category=models.CharField(max_length=15,choices=CATEGORY_CHOICES)
    sub_category=models.ForeignKey(SubCategory,on_delete=models.CASCADE)
    class Meta:
        unique_together = (("date", "daytoken"),)

class Reply(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    grievance=models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='reply')
    date_time=models.DateTimeField(auto_now_add=True)
    message=models.TextField(max_length=1000)