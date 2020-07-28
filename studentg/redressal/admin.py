from django.contrib import admin
# Register your models here.
from django.forms.models import ModelForm

from redressal.models import University, RedressalBody, Institute, Department


class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        """ Should returns True if data differs from initial.
        By always returning true even unchanged inlines will get validated and saved."""
        return True


class UniversityInline(admin.StackedInline):
    model = University
    min_num = 0
    max_num = 1
    form = AlwaysChangedModelForm


class InstituteInline(admin.StackedInline):
    model = Institute
    min_num = 0
    max_num = 1


class DepartmentInline(admin.StackedInline):
    model = Department
    min_num = 0
    max_num = 1


class RedressalBodyAdmin(admin.ModelAdmin):
    inlines = [UniversityInline, InstituteInline, DepartmentInline]


admin.site.register(RedressalBody, RedressalBodyAdmin)
admin.site.register(University)
