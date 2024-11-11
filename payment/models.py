import uuid
from django.db import models
from django.conf import settings
class Wallet(models.Model):
    currency = models.CharField(max_length=10)  # e.g., 'BTC', 'ETH', etc.
    address = models.CharField(max_length=100)

    def _str_(self):
        return f"{self.currency} Wallet"

class UserBalance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def _str_(self):
        return f"{self.user.username} Balance"

class PaymentConfirmation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10)
    transaction_id = models.CharField(max_length=100, unique=True, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_submitted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='Pending')

    def save(self, *args, **kwargs):
        if not self.transaction_id:  # Generate a unique transaction_id if not already set
            self.transaction_id = str(uuid.uuid4())  # Generates a UUID and converts it to a string
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} Payment - {self.amount} {self.currency} - {self.status}"
