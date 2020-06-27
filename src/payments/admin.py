from django.contrib import admin

from .models import Currency, Wallet, Transaction, ExchangeRate


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    fields = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user', 'currency')
    list_display = ('name', 'currency', 'user')
    fields = ('name', 'user', 'currency', 'balance')
    search_fields = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    autocomplete_fields = ('from_user', 'to_user', 'currency')
    list_display = (
        'from_user',
        'to_user',
        'currency',
        'amount',
        'status',
    )
    fields = (
        'from_user',
        'to_user',
        'currency',
        'amount',
        'status',
        'paid_at',
    )
    readonly_fields = ('paid_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('from_user', 'to_user')


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    autocomplete_fields = ('from_currency', 'to_currency',)
    list_display = ('from_currency', 'to_currency', 'amount')
    fields = ('from_currency', 'to_currency', 'amount')
