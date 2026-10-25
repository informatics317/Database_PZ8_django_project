from django.conf import settings
from django.db import models


class Equipment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    total = models.PositiveIntegerField()
    available = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Booking(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Создана"
        CONFIRMED = "confirmed", "Подтверждена"
        COMPLETED = "completed", "Завершена"
        CANCELLED = "cancelled", "Отменена"

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="bookings"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    quantity = models.PositiveIntegerField(default=1)
    purpose = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Бронирование №{self.id}"


class BookingEvent(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="events"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="booking_events"
    )
    action = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking_id}: {self.action}"
