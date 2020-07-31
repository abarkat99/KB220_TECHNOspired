from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

# Register your models here.
from accounts.models import User, Student, UniversityMember, InstituteMember, DepartmentMember, TempUser, StudentTempUser


class StudentTempUserInline(admin.StackedInline):
    model = StudentTempUser
    min_num = 1
    max_num = 1


class TempUserAdmin(admin.ModelAdmin):
    exclude = ('uidb64', 'token')
    inlines = [StudentTempUserInline]

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        unfiltered = super(TempUserAdmin, self).get_inline_instances(request, obj)
        if obj.designation == TempUser.STUDENT:
            return [x for x in unfiltered if isinstance(x, StudentTempUserInline)]
        return []



class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('designation',)


class StudentInline(admin.StackedInline):
    model = Student
    min_num = 1
    max_num = 1


class UniversityMemberInline(admin.StackedInline):
    model = UniversityMember
    min_num = 1
    max_num = 1


class InstituteMemberInline(admin.StackedInline):
    model = InstituteMember
    min_num = 1
    max_num = 1


class DepartmentMemberInline(admin.StackedInline):
    model = DepartmentMember
    min_num = 1
    max_num = 1


ADDITIONAL_USER_FIELDS = (
    (None, {'fields': ('designation',)}),
)


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    fieldsets = UserAdmin.fieldsets + ADDITIONAL_USER_FIELDS
    add_fieldsets = UserAdmin.add_fieldsets + ADDITIONAL_USER_FIELDS
    inlines = [StudentInline, UniversityMemberInline, InstituteMemberInline, DepartmentMemberInline]

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        unfiltered = super(MyUserAdmin, self).get_inline_instances(request, obj)
        if obj.designation == User.STUDENT:
            return [x for x in unfiltered if isinstance(x, StudentInline)]
        elif obj.designation in [User.UNIVERSITY, User.UNI_HEAD]:
            return [x for x in unfiltered if isinstance(x, UniversityMemberInline)]
        elif obj.designation in [User.INSTITUTE, User.INS_HEAD]:
            return [x for x in unfiltered if isinstance(x, InstituteMemberInline)]
        elif obj.designation in [User.DEPARTMENT, User.DEP_HEAD]:
            return [x for x in unfiltered if isinstance(x, DepartmentMemberInline)]
        return []


admin.site.register(User, MyUserAdmin)
admin.site.register(TempUser, TempUserAdmin)
