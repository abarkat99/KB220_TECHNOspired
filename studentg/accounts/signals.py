from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Student, UniversityMember, InstituteMember, DepartmentMember, TempUser


@receiver(post_delete, sender=Student)
@receiver(post_delete, sender=UniversityMember)
@receiver(post_delete, sender=InstituteMember)
@receiver(post_delete, sender=DepartmentMember)
def auto_delete_user_with_designation_object(sender, instance, *args, **kwargs):
    instance.user.delete()


@receiver(post_save, sender=TempUser)
def auto_send_mail(sender, instance, created, *args, **kwargs):
    if created:
        instance.send_mail()