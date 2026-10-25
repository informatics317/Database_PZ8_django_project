from rest_framework import serializers

from accounts.views import is_methodist
from .models import Booking, BookingEvent, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ("id", "name", "total", "available")


class BookingSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(
        source="equipment.name", read_only=True
    )
    owner_name = serializers.CharField(
        source="owner.username", read_only=True
    )
    status_text = serializers.CharField(
        source="get_status_display", read_only=True
    )
    can_manage = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            "id",
            "equipment",
            "equipment_name",
            "owner_name",
            "quantity",
            "purpose",
            "status",
            "status_text",
            "can_manage",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")

    def get_can_manage(self, booking):
        user = self.context["request"].user
        return user.is_superuser or is_methodist(user)

    def validate_purpose(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Цель должна содержать не менее 5 символов."
            )
        return value.strip()

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Количество должно быть не меньше 1."
            )
        return value

    def validate(self, attrs):
        if (self.instance is not None
                and self.instance.status != Booking.Status.CREATED):
            raise serializers.ValidationError(
                "Изменять можно только бронирование в статусе «Создана»."
            )

        equipment = attrs.get("equipment")
        quantity = attrs.get("quantity")

        if self.instance is not None:
            equipment = equipment or self.instance.equipment
            quantity = quantity or self.instance.quantity

        if equipment and quantity and quantity > equipment.total:
            raise serializers.ValidationError({
                "quantity": f"Всего есть только {equipment.total} шт."
            })

        return attrs


class BookingEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(
        source="actor.username", read_only=True, default="система"
    )

    class Meta:
        model = BookingEvent
        fields = ("id", "action", "actor_name", "created_at")
