from unittest.mock import patch

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Booking, BookingEvent, Equipment
from .services import change_status


class BookingTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin1", password="pass12345")
        self.student = User.objects.create_user("student1", password="pass12345")
        self.projector = Equipment.objects.create(name="Проектор", total=3, available=3)

        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/bookings/",
            {"equipment": self.projector.id, "quantity": 2,
             "purpose": "Защита проекта"},
            format="json",
        )
        self.booking_id = response.data["id"]

    # Запрещённый переход отклоняется
    def test_second_confirm_is_rejected(self):
        self.client.force_authenticate(self.admin)
        self.client.post(f"/api/bookings/{self.booking_id}/confirm/")
        response = self.client.post(f"/api/bookings/{self.booking_id}/confirm/")
        self.assertEqual(response.status_code, 400)
        self.projector.refresh_from_db()
        self.assertEqual(self.projector.available, 1)      # остаток не изменился
        self.assertEqual(BookingEvent.objects.count(), 2)  # история не изменилась

    # При сбое не сохраняется ни одна часть операции
    def test_failure_rolls_back_everything(self):
        with patch.object(BookingEvent.objects, "create",
                          side_effect=RuntimeError("Имитация сбоя")):
            with self.assertRaises(RuntimeError):
                change_status(self.booking_id, "confirm", self.admin)
        self.projector.refresh_from_db()
        self.assertEqual(self.projector.available, 3)
        self.assertEqual(Booking.objects.get(pk=self.booking_id).status, "created")
        self.assertEqual(BookingEvent.objects.count(), 1)




