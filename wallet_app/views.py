from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from wallet_app.models import Wallet
from wallet_app.serializers import WalletSerializer


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

    def create(self, request, *args, **kwargs):  # necessary for debugging
        return super().create(request, *args, **kwargs)
