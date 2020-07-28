from django.db import models
from accounts.models import User
from studentg.models import Grievance

# Create your models here.


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    grievance = models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='notifications')
