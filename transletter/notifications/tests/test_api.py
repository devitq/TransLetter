from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
import parameterized

from accounts.models import User
from notifications.models import Notification

__all__ = ()


class NotificationsCreatingTests(TestCase):
    test_order = "defined"
    fixtures = ["notifications/fixtures/initdata.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(
            username="testuser",
        )
        Notification.objects.create(
            user=cls.user,
            title="AnyTitle",
            content="AnyContent",
        )
        Notification.objects.create(
            user=cls.user,
            title="OtherAnyTitle",
            content="OtherAnyContent",
        )

    def setUp(self):
        self.client.force_login(self.user)

    @parameterized.parameterized.expand(
        [
            ([1, 2]),
            ([1]),
        ],
    )
    def test_notifications_read_by_apy(self, *data):
        url = reverse("notifications:read_notifications")
        for notification in Notification.objects.filter(id__in=data):
            self.assertFalse(notification.read)
        response = self.client.post(
            url,
            {"notification_ids": ",".join(map(str, data))},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for notification in Notification.objects.filter(id__in=data):
            self.assertTrue(notification.read)
