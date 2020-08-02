from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Notification


@receiver(post_save, sender=Notification)
def auto_send_mail(sender, instance, created, *args, **kwargs):
    if created:
        if instance.user.designation == instance.user.STUDENT:
            instance.send_mail()
        else:
            instance.redressal_send_mail()
