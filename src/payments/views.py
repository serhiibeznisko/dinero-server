from drf_yasg.utils import swagger_auto_schema

from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.response import Response

from .models import Transaction, Wallet, Currency, ExchangeRate
from .serializers import (
    WalletSerializer,
    TransactionSerializer,
    CurrencySerializer,
    ExchangeRateSerializer,
    ExchangeCurrencySerializer,
)
from core.enums import TransactionStatus


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='[Currencies List] Retrieve a list of all the available currencies.',
))
class CurrencyListAPIView(generics.ListAPIView):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()
    pagination_class = None


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='[Exchange Rates List] Retrieve a list of all the current exchange rates.',
))
class ExchangeRateListAPIView(generics.ListAPIView):
    serializer_class = ExchangeRateSerializer
    queryset = ExchangeRate.objects.all()
    pagination_class = None


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='[Wallet List] Retrieve a list of your own wallets.',
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='[Create Wallet] Create a new wallet with given currency.',
))
class WalletListAPIView(generics.ListCreateAPIView):
    serializer_class = WalletSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return Wallet.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='[Wallet Details] Retrieve a detailed information about your wallet.',
))
@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary='[Update Wallet] Update your wallet balance.',
))
@method_decorator(name='patch', decorator=swagger_auto_schema(
    operation_summary='[Update Wallet] Update your wallet balance.',
))
class WalletAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = WalletSerializer

    def get_queryset(self):
        user = self.request.user
        return Wallet.objects.filter(user=user)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='[Transaction List] Retrieve a list of your transaction history.',
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='[Create Wallet] Create a new transaction.',
))
class TransactionListAPIView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(
            Q(from_user=user) |
            Q(to_user=user)
        )

    def perform_create(self, serializer):
        user = self.request.user
        transaction = serializer.save(
            from_user=user,
            status=TransactionStatus.SUCCESSFUL,
            paid_at=timezone.now(),
        )
        self.perform_transaction(transaction)

    def perform_transaction(self, transaction):
        from_wallet = Wallet.objects.get(user=transaction.from_user, currency=transaction.currency)
        to_wallet = Wallet.objects.get(user=transaction.to_user, currency=transaction.currency)
        from_wallet.update(balance=from_wallet.balance - transaction.amount)
        to_wallet.update(balance=to_wallet.balance + transaction.amount)


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='[Exchange Currency] Exchange currency between your wallets.',
))
class ExchangeCurrencyAPIView(generics.GenericAPIView):
    serializer_class = ExchangeCurrencySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        self.perform_exchange(data)
        return Response(serializer.data)

    def perform_exchange(self, data):
        from_wallet = data['from_wallet']
        to_wallet = data['to_wallet']
        from_amount = data['from_amount']
        exchange_rate = generics.get_object_or_404(
            ExchangeRate,
            from_currency=from_wallet.currency,
            to_currency=to_wallet.currency,
        )
        to_amount = from_amount * exchange_rate.amount
        from_wallet.update(balance=from_wallet.balance - from_amount)
        to_wallet.update(balance=to_wallet.balance + to_amount)
