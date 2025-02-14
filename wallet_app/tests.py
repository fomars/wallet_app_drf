from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from wallet_app.models import Wallet


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def wallets():
    return [
        Wallet.objects.create(label="Wallet A", balance=Decimal("100.0")),
        Wallet.objects.create(label="Wallet B", balance=Decimal("200.0")),
        Wallet.objects.create(label="Test C", balance=Decimal("300.0")),
    ]


@pytest.mark.django_db
class TestWalletViewSet:
    URL_LIST: str = reverse("wallet-list")

    def test_get_wallet(self, api_client, wallets):
        url = reverse("wallet-detail", args=[wallets[0].id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert (response.data["id"], response.data["label"]) == (
            wallets[0].id,
            wallets[0].label,
        )

    def test_delete_wallet(self, api_client, wallets):
        url = reverse("wallet-detail", args=[wallets[0].id])
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        resp = api_client.get(self.URL_LIST)
        assert len(resp.data["results"]) - len(wallets) == -1

    def test_list_wallets(self, api_client, wallets):
        response = api_client.get(self.URL_LIST)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_filter_by_balance(self, api_client, wallets):
        response = api_client.get(self.URL_LIST + "?balance__gt=150")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_filter_by_label(self, api_client, wallets):
        response = api_client.get(self.URL_LIST + "?label__icontains=wallet")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_ordering(self, api_client, wallets):
        response = api_client.get(self.URL_LIST + "?ordering=-balance")
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data["results"][0]["balance"]) == Decimal("300.0")

    @pytest.mark.parametrize(
        "label, balance, response_code",
        [
            ("ciento", 100, status.HTTP_201_CREATED),
            ("cero", 0, status.HTTP_201_CREATED),
            ("invalido", -1, status.HTTP_400_BAD_REQUEST),
        ],
    )
    def test_create_wallet(self, api_client, label, balance, response_code):
        data = {
            "data": {
                "type": "Wallet",
                "attributes": {"label": label, "balance": balance},
            }
        }
        response = api_client.post(self.URL_LIST, data)
        assert response.status_code == response_code
        # check created
        results = api_client.get(self.URL_LIST).data["results"]
        if balance >= 0:
            assert len(results) > 0
            assert (results[0]["label"], Decimal(results[0]["balance"])) == (
                label,
                balance,
            )
        else:
            assert len(results) == 0
