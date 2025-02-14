import concurrent
from decimal import Decimal

import pytest
from django.test import TransactionTestCase
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient

from wallet_app.models import Wallet

fake = Faker()


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


def create_wallet(label: str = None, balance: Decimal = None) -> Wallet:
    wallet = Wallet.objects.create(
        label=label or fake.company(),
        balance=(
            balance
            if balance is not None
            else fake.pydecimal(min_value=0, max_value=10000000, right_digits=8)
        ),
    )
    return wallet


@pytest.fixture
def wallet_factory() -> callable:
    return create_wallet


@pytest.mark.django_db
class TestWalletViewSet:
    URL: str = reverse("wallet-list")

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
        resp = api_client.get(self.URL)
        assert len(resp.data["results"]) - len(wallets) == -1

    def test_list_wallets(self, api_client, wallets):
        response = api_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_filter_by_balance(self, api_client, wallets):
        response = api_client.get(self.URL + "?balance__gt=150")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_filter_by_label(self, api_client, wallets):
        response = api_client.get(self.URL + "?label__icontains=wallet")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_ordering(self, api_client, wallets):
        response = api_client.get(self.URL + "?ordering=-balance")
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
        response = api_client.post(self.URL, data)
        assert response.status_code == response_code
        # check created
        results = api_client.get(self.URL).data["results"]
        if balance >= 0:
            assert len(results) > 0
            assert (results[0]["label"], Decimal(results[0]["balance"])) == (
                label,
                balance,
            )
        else:
            assert len(results) == 0


@pytest.mark.django_db
class TestTransaction:
    URL: str = reverse("transaction-list")

    @pytest.mark.parametrize(
        "init_bal, tx_amt",
        [(0, 0), (0, 100), (100, 0), (100, 100), (100, -1), (100, -100)],
    )
    def test_create_valid(self, api_client, wallet_factory, init_bal, tx_amt):
        test_wallet = wallet_factory(balance=init_bal)
        data = {
            "data": {
                "type": "Transaction",
                "attributes": {"amount": tx_amt, "wallet": test_wallet.id},
            }
        }
        response = api_client.post(self.URL, data)
        assert response.status_code == 201

        test_wallet.refresh_from_db()
        assert test_wallet.balance == init_bal + tx_amt

    @pytest.mark.parametrize(
        "init_bal, tx_amt",
        [
            (0, -1),
            (0, -0.00000001),
            (99, -100),
            (100, -1000000000),
        ],
    )
    def test_insuff_balance(self, api_client, wallet_factory, init_bal, tx_amt):
        test_wallet = wallet_factory(balance=init_bal)
        data = {
            "data": {
                "type": "Transaction",
                "attributes": {"amount": tx_amt, "wallet": test_wallet.id},
            }
        }
        response = api_client.post(self.URL, data)
        assert response.status_code == 400
        test_wallet.refresh_from_db()
        assert test_wallet.balance == init_bal


class TestTransactionConcurrency(TransactionTestCase):
    URL = TestTransaction.URL

    def setUp(self):
        self.client = APIClient()

    def test_concurrent_transactions(self):
        init_bal = 1000
        txs_amts = [+105, -55, +99, -101] * 100
        expected_bal = init_bal + sum(txs_amts)
        wallet = create_wallet(balance=init_bal)
        wallet_id = str(wallet.id)

        def send_tx(tx_amt):
            resp = self.client.post(
                self.URL,
                {
                    "data": {
                        "type": "Transaction",
                        "attributes": {"amount": tx_amt, "wallet": wallet_id},
                    }
                },
            )
            return resp

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(send_tx, amt) for amt in txs_amts]

        for future in concurrent.futures.as_completed(futures):
            response = future.result()
            if response.status_code != 201:
                print(response)
            assert response.status_code == 201

        wallet.refresh_from_db()
        assert wallet.balance == expected_bal
