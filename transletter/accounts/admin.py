from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
import django.contrib.auth.models

from accounts.forms import CreateUserAdminForm, EditUserAdminForm
from accounts.models import Account

__all__ = ()


class AccountInline(admin.TabularInline):
    model = Account
    can_delete = False
    readonly_fields = (Account.attempts_count.field.name,)


class UserAdmin(BaseUserAdmin):
    inlines = (AccountInline,)
    form = EditUserAdminForm
    add_form = CreateUserAdminForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )


admin.site.unregister(django.contrib.auth.models.User)
admin.site.register(django.contrib.auth.models.User, UserAdmin)
