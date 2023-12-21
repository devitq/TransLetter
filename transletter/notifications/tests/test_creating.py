from django.test import TestCase

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

    def setUp(self):
        self.client.force_login(self.user)

    def test_creation(self):
        count = Notification.objects.filter(user=self.user).count()
        self.user.add_notification("AnyTitle", "AnyContent")
        self.user.add_notification(
            title="OtherAnyTitle",
            content="OtherAnyContent",
        )
        self.assertEqual(
            Notification.objects.filter(user=self.user).count(),
            count + 2,
        )
