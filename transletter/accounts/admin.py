from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
import django.contrib.auth.models
from django.utils.translation import gettext_lazy as _

from accounts.forms import CreateUserAdminForm, EditUserAdminForm
from accounts.models import Account

__all__ = ()

admin.site.site_header = _("TransLetter Admin")
admin.site.site_title = _("TransLetter Admin")
admin.site.index_title = _("TransLetter Admin")


class AccountInline(admin.StackedInline):
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
