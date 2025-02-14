import uuid

from django.contrib.postgres.indexes import BTreeIndex
from django.db import models, transaction
from django.db.models.functions import Now

BALANCE_CONSTRAINT_NAME = "non_negative_balance"


class Wallet(models.Model):
    label = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(db_default=Now(), auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gte=0),
                name=BALANCE_CONSTRAINT_NAME,
            )
        ]


class Transaction(models.Model):
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    txid = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    created_at = models.DateTimeField(db_default=Now())

    class Meta:
        indexes = [
            BTreeIndex(fields=["txid"]),
            BTreeIndex(fields=["wallet"]),
            BTreeIndex(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(id=self.wallet_id)
            wallet.balance += self.amount
            wallet.save()
            super().save(*args, **kwargs)
