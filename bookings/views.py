from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.views import is_methodist
from .models import Booking, BookingEvent, Equipment
from .serializers import (BookingEventSerializer, BookingSerializer, EquipmentSerializer,)
from .services import change_status


def can_manage(user):
    return user.is_superuser or is_methodist(user)


@login_required(login_url="/accounts/login/")
@ensure_csrf_cookie
def bookings_page(request):
    return render(request, "bookings/bookings.html")


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Equipment.objects.all().order_by("name")
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Booking.objects.select_related("equipment", "owner")

        if not can_manage(self.request.user):
            queryset = queryset.filter(owner=self.request.user)

        if self.action == "list":
            status = self.request.query_params.get("status")
            equipment = self.request.query_params.get("equipment")

            if status:
                queryset = queryset.filter(status=status)
            if equipment and equipment.isdigit():
                queryset = queryset.filter(equipment_id=equipment)

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        with transaction.atomic():
            booking = serializer.save(owner=self.request.user)
            BookingEvent.objects.create(
                booking=booking,
                actor=self.request.user,
                action="Бронирование создано"
            )

    def perform_update(self, serializer):
        with transaction.atomic():
            booking = serializer.save()
            BookingEvent.objects.create(
                booking=booking,
                actor=self.request.user,
                action="Данные бронирования изменены"
            )

    def perform_destroy(self, instance):
        if instance.status not in (
                Booking.Status.CREATED, Booking.Status.CANCELLED
        ):
            raise ValidationError(
                "Удалять можно только бронирование "
                "в статусе «Создана» или «Отменена»."
            )
        instance.delete()

    def run_action(self, request, name):
        booking = self.get_object()

        if name in ("confirm", "complete") and not can_manage(request.user):
            raise PermissionDenied(
                "Подтверждать и завершать бронирования "
                "может только методист или администратор."
            )

        booking = change_status(booking.pk, name, request.user)
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        return self.run_action(request, "confirm")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        return self.run_action(request, "complete")

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        return self.run_action(request, "cancel")

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        booking = self.get_object()
        events = booking.events.select_related("actor").order_by("created_at", "id")
        return Response(BookingEventSerializer(events, many=True).data)




