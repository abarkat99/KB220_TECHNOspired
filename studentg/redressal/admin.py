from django.contrib import admin
# Register your models here.
from django.forms.models import ModelForm

from redressal.models import University, RedressalBody, Institute, Department, SubCategory


class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        """ Should returns True if data differs from initial.
        By always returning true even unchanged inlines will get validated and saved."""
        return True


class UniversityInline(admin.StackedInline):
    model = University
    min_num = 1
    max_num = 1
    form = AlwaysChangedModelForm


class InstituteInline(admin.StackedInline):
    model = Institute
    min_num = 1
    max_num = 1


class DepartmentInline(admin.StackedInline):
    model = Department
    min_num = 1
    max_num = 1


class RedressalBodyAdmin(admin.ModelAdmin):
    inlines = [UniversityInline, InstituteInline, DepartmentInline]

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        unfiltered = super(RedressalBodyAdmin, self).get_inline_instances(request, obj)
        if obj.body_type == RedressalBody.UNIVERSITY:
            return [x for x in unfiltered if isinstance(x, UniversityInline)]
        elif obj.body_type == RedressalBody.INSTITUTE:
            return [x for x in unfiltered if isinstance(x, InstituteInline)]
        elif obj.body_type == RedressalBody.DEPARTMENT:
            return [x for x in unfiltered if isinstance(x, DepartmentInline)]
        return []


admin.site.register(RedressalBody, RedressalBodyAdmin)
admin.site.register(SubCategory)
