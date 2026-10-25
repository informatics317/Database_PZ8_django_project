from django.contrib import admin
from .models import Booking, BookingEvent, Equipment


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "total", "available")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "equipment", "owner", "quantity", "status", "created_at")
    list_filter = ("status", "equipment")


@admin.register(BookingEvent)
class BookingEventAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "action", "actor", "created_at")

