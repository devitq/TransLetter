from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from notifications.models import Notification

__all__ = ()


class NotificationsView(LoginRequiredMixin, ListView):
    template_name = "notifications/notifications.html"
    paginate_by = 5
    model = Notification

    def get_queryset(self):
        return Notification.objects.by_user(self.request.user.id).order_by(
            "-created_at",
        )
