from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Category, Ticket
from .serializers import (
    CategorySerializer,
    TicketSerializer,
)
from accounts.views import is_methodist
from rest_framework.exceptions import PermissionDenied

@login_required(login_url="/accounts/login/")
@ensure_csrf_cookie
def dashboard(request):
    return render(request, "tickets/dashboard.html")

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Ticket.objects.filter(
            owner=self.request.user
        ).select_related("category")

        user = self.request.user
        if user.is_superuser or is_methodist(user):
            queryset = Ticket.objects.select_related("category")
        queryset = queryset.select_related("owner")

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


