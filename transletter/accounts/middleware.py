from django.core.exceptions import PermissionDenied

import accounts.models

__all__ = ("Accounts",)


class Accounts:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user = (
                accounts.models.User.objects.filter(pk=request.user.pk)
                .select_related("account")
                .first()
            )
            if user.account.blocked:
                raise PermissionDenied()
            request.user = user
        return self.get_response(request)
