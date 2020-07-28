from django.contrib import admin

# Register your models here.
from accounts.models import TempUser


class TempUserAdmin(admin.ModelAdmin):
    exclude = ('uidb64', 'token')


admin.site.register(TempUser, TempUserAdmin)
