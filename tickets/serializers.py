from rest_framework import serializers
from .models import Category, Ticket
from accounts.views import is_methodist

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class TicketSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )
    owner_name = serializers.CharField(
        source="owner.username",
        read_only=True
    )
    can_manage = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = (
            "id",
            "title",
            "description",
            "category",
            "category_name",
            "can_manage",
            "owner_name",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_can_manage(self, ticket):
        user = self.context["request"].user
        return user.is_superuser or is_methodist(user)

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Название должно содержать "
                "не менее 5 символов."
            )
        return value.strip()

    def validate(self, attrs):
        if self.instance is None:
            if attrs.get("status", Ticket.Status.NEW) != Ticket.Status.NEW:
                raise serializers.ValidationError({
                    "status": "Новая заявка должна иметь статус «Новая»."
                })
            return attrs

        old_status = self.instance.status
        new_status = attrs.get("status", old_status)

        allowed = {
            Ticket.Status.NEW: {Ticket.Status.PROGRESS},
            Ticket.Status.PROGRESS: {Ticket.Status.DONE},
            Ticket.Status.DONE: set(),
        }

        if new_status != old_status:
            if new_status not in allowed[old_status]:
                raise serializers.ValidationError({
                    "status": "Недопустимый переход статуса."
                })

        return attrs
