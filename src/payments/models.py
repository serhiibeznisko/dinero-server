from django.db import models

from accounts.models import User
from core.enums import TransactionStatus
from core.mixins import UpdateMixin
from core.models import CreatedUpdatedModel


class Currency(CreatedUpdatedModel):
    name = models.CharField(max_length=32, unique=True)
    code = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Currencies'
        ordering = ('name',)


class Wallet(CreatedUpdatedModel, UpdateMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_set')
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='wallet_set')
    balance = models.FloatField(default=0)

    class Meta:
        unique_together = ('user', 'currency')


class Transaction(CreatedUpdatedModel):
    from_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='from_transaction_set')
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='to_transaction_set')
    amount = models.FloatField(default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='transaction_set')
    status = models.CharField(max_length=15, choices=TransactionStatus)
    paid_at = models.DateTimeField()

    class Meta:
        ordering = ('-id',)


class ExchangeRate(CreatedUpdatedModel):
    from_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='from_currency_rate_set')
    to_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='to_currency_rate_set')
    amount = models.FloatField(default=0)
