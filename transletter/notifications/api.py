from http import HTTPStatus

from django.http import JsonResponse

from notifications.models import Notification


__all__ = ()


def read_notifications(request):
    if request.method == "POST":
        try:
            notification_ids = request.POST.get("notification_ids", []).split(
                ",",
            )
            if notification_ids == [""]:
                notification_ids = []

            Notification.objects.by_user(request.user.id).filter(
                id__in=notification_ids,
            ).update(read=True)

            return JsonResponse({"status": "success"})
        except Exception:
            return JsonResponse(
                {"status": "error", "message": "Invalid request"},
                status=HTTPStatus.BAD_REQUEST,
            )

    return JsonResponse(
        {"status": "error", "message": "Invalid request method"},
        status=HTTPStatus.BAD_REQUEST,
    )
