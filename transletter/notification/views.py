from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from notification.models import Notification

__all__ = ()


class NotificationsView(LoginRequiredMixin, ListView):
    template_name = "notification/notifications.html"
    paginate_by = 10
    model = Notification
    context_object_name = "notifications"

    def get_queryset(self):
        return Notification.objects.by_user(self.request.user.id).order_by(
            "-id",
        )
