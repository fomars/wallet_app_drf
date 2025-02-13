from rest_framework import serializers

from wallet_app.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "label", "balance", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, data):
        if "balance" in data and data["balance"] < 0:
            raise serializers.ValidationError(
                {"balance": "Balance must be non-negative"}
            )
        return data
