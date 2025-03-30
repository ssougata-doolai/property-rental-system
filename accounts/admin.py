from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Profile, EmailOTP, PhoneCountryCode, PhoneOTP, UserEmail
from .forms import PermissionChangeListForm
from django.contrib.admin.views.main import ChangeList

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    #The fields to be used in displaying the User model.
    list_display = ('phone_number', 'staff', 'is_superuser',)
    list_filter = ('staff', 'active', 'is_superuser',)
    ordering = ('phone_number',)
    filter_horizontal = ()
    fieldsets = (
        (None,{'fields':('phone_number','password')}),
        ('Permissions',{'fields':('active', 'staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes':('wide'),
            'fields':('phone_number', 'password1', 'password2')
        }),
    )

class PhoneCountryCodeAdmin(admin.ModelAdmin):
    list_display = ['name','dial_code', 'code']
    ordering = ('name',)

    class Meta:
        model = PhoneCountryCode

class UserEmailInline(admin.TabularInline):
    model = UserEmail

class ProfileAdmin(admin.ModelAdmin):
    inlines = [UserEmailInline, ]
    class Meta:
        model = Profile

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(PhoneOTP)
admin.site.register(EmailOTP)
admin.site.register(UserEmail)
admin.site.register(PhoneCountryCode, PhoneCountryCodeAdmin)
