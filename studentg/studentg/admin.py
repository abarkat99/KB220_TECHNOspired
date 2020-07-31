from django.contrib import admin
from .models import Grievance, Reply, Notification
# Register your models here.
admin.site.register(Grievance)
admin.site.register(Reply)
admin.site.register(Notification)
