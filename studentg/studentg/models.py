from django.db import models
from django.db import transaction
from django.core.mail import send_mail
from accounts.models import User
import datetime
from redressal.models import SubCategory, RedressalBody
from .constants import StatusConstants
from django_hosts.resolvers import reverse


# Concurrency controlled generation of tokens Singleton table
class DayToken(models.Model):
    counter = models.IntegerField(default=0)
    last_update = models.DateField(auto_now_add=True)

    @classmethod
    def get_new_token(cls):
        with transaction.atomic():
            daytoken = cls.objects.select_for_update().first()
            if daytoken == None:
                daytoken = cls()
            if daytoken.last_update != datetime.date.today():
                daytoken.last_update = datetime.date.today()
                daytoken.counter = 0
            daytoken.counter = daytoken.counter + 1
            daytoken.save()
            return daytoken.counter

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(DayToken, self).save(*args, **kwargs)


class Grievance(StatusConstants, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grievances')
    date = models.DateField(auto_now_add=True)
    redressal_body = models.ForeignKey(RedressalBody, on_delete=models.CASCADE, related_name='grievances')
    daytoken = models.IntegerField()

    last_update = models.DateField(auto_now=True)
    status = models.PositiveSmallIntegerField(choices=StatusConstants.STATUS_CHOICES, default=StatusConstants.REVIEW)
    message = models.TextField(max_length=1000)
    subject = models.CharField(max_length=255)
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    UNIVERSITY = 1
    INSTITUTE = 2
    DEPARTMENT = 3
    CATEGORY_CHOICES = [
        (UNIVERSITY, 'University'),
        (INSTITUTE, 'Institute'),
        (DEPARTMENT, 'Department'),
    ]
    category = models.PositiveSmallIntegerField(choices=CATEGORY_CHOICES)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("date", "daytoken"),)
        ordering = ['-last_update']

    def __str__(self):
        return f'{self.subject} - ({self.pk})'
    
    def token(self):
        return self.date.strftime('%Y%m%d') + str(self.daytoken).zfill(4)
    
    def status_html_class(self):
        return self.STATUS_COLORS[self.status]

    def get_escalated_level_display(self):
        escalator = {
            self.DEPARTMENT: 'Institute',
            self.INSTITUTE: 'University'
        }
        return escalator[self.category]

    @classmethod
    def get_from_token(cls, token):
        date = datetime.datetime.strptime(token[:-4], "%Y%m%d").date()
        daytoken = int(token[-4:])
        try:
            grievance = cls.objects.get(date=date, daytoken=daytoken)
        except cls.DoesNotExist:
            grievance = None
        return grievance


class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grievance = models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='reply')
    date_time = models.DateTimeField(auto_now_add=True)
    message = models.TextField(max_length=1000)

    class Meta:
        ordering = ['date_time']
        verbose_name_plural = "Replies"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    grievance = models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='notifications')
    date_time = models.DateTimeField(auto_now_add=True)

    def send_mail(self):
        token_no = self.grievance.token()
        url = reverse('view_grievance', host='www', kwargs={
            'token': token_no
        })
        send_mail(
            f'Your Grievance No. {token_no}',
            f'There has been some action on your grievance: click this link to check it out: http:{url}',
            'st050100@gmail.com',
            [self.user.email],
            fail_silently=False,
        )

    def redressal_send_mail(self):
        token_no = self.grievance.token()
        url = reverse('view_grievance', host='redressal', kwargs={
            'token': token_no
        })
        send_mail(
            f'New Grievance having No. {token_no}',
            f'There is a new grievance: click this link to check it out: http:{url}',
            'st050100@gmail.com',
            [self.user.email],
            fail_silently=False,
        )


class Rating(models.Model):
    grievance = models.OneToOneField(Grievance, on_delete=models.CASCADE, related_name='rating')
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    RATING_CHOICES = [
        (FIVE, '5 Stars'),
        (FOUR, '4 Stars'),
        (THREE, '3 Stars'),
        (TWO, '2 Stars'),
        (ONE, '1 Star'),
    ]
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)

    def get_lacking_score(self):
        return 5 - self.rating
