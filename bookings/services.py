from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Booking, BookingEvent, Equipment

TRANSITIONS = {
    "confirm": (Booking.Status.CREATED, Booking.Status.CONFIRMED),
    "complete": (Booking.Status.CONFIRMED, Booking.Status.COMPLETED),
    "cancel": (Booking.Status.CREATED, Booking.Status.CANCELLED),
}


EVENT_TEXT = {
    "confirm": "Подтверждена (оборудование выдано)",
    "complete": "Завершена (оборудование возвращено)",
    "cancel": "Отменена",
}


def change_status(booking_id, action, user):
    from_status, to_status = TRANSITIONS[action]

    with transaction.atomic():
        booking = Booking.objects.get(pk=booking_id)
        equipment = booking.equipment

        if booking.status != from_status:
            raise ValidationError("Недопустимый переход статуса.")

        if action == "confirm":
            if equipment.available < booking.quantity:
                raise ValidationError(
                    "Недостаточно свободного оборудования. "
                    f"Свободно: {equipment.available}."
                )
            equipment.available -= booking.quantity
            equipment.save()

        if action == "complete":
            equipment.available += booking.quantity
            equipment.save()

        booking.status = to_status
        booking.save()

        BookingEvent.objects.create(
            booking=booking,
            actor=user,
            action=EVENT_TEXT[action]
        )

    return booking
