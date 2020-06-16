from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('currencies', views.CurrencyListAPIView.as_view()),
    path('exchange-rates', views.ExchangeRateListAPIView.as_view()),
    path('exchange-currency', views.ExchangeCurrencyAPIView.as_view()),
    path('wallets', views.WalletListAPIView.as_view()),
    path('wallets/<int:pk>', views.WalletAPIView.as_view()),
    path('transactions', views.TransactionListAPIView.as_view()),
]
