from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter

from wallet_app.models import BALANCE_CONSTRAINT_NAME, Transaction, Wallet
from wallet_app.serializers import TransactionSerializer, WalletSerializer


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "label": ["exact", "icontains"],
        "balance": ["gt", "lt", "exact"],
        "id": ["exact"],
    }
    ordering_fields = ["id", "label", "balance", "created_at"]
    ordering = ["-created_at"]

    def create(self, request, *args, **kwargs):  # for debugging
        return super().create(request, *args, **kwargs)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["wallet", "txid"]
    ordering_fields = ["created_at", "amount"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError as e:
            if BALANCE_CONSTRAINT_NAME in str(e):
                raise ValidationError("Insufficient balance")
            raise
