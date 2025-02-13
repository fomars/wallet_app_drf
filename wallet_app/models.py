from django.db import models
from django.db.models.functions import Now


class Wallet(models.Model):
    label = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=36, decimal_places=18, default=0)
    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(db_default=Now(), auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gte=0),
                name="non_negative_balance",
            )
        ]
