from rest_framework import serializers, generics

from .models import Currency, Wallet, Transaction, ExchangeRate
from accounts.models import User
from accounts.serializers.users import UserPKField


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = (
            'name',
            'code',
        )


class ExchangeRateSerializer(serializers.ModelSerializer):
    from_currency = CurrencySerializer()
    to_currency = CurrencySerializer()

    class Meta:
        model = ExchangeRate
        fields = (
            'from_currency',
            'to_currency',
            'amount',
            'updated_at',
        )


class CurrencyPKField(serializers.SlugRelatedField):
    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        serializer = CurrencySerializer(value)
        return serializer.data


class WalletSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    currency = CurrencyPKField(
        queryset=Currency.objects.all(),
        slug_field='code',
    )
    name = serializers.CharField(max_length=64)
    balance = serializers.FloatField(min_value=0)

    def validate_currency(self, value):
        user = self.context['request'].user
        if Wallet.objects.filter(user=user, currency=value).exists():
            raise serializers.ValidationError('Wallet with given currency already exists.')

        return value

    def update(self, instance, validated_data):
        validated_data.pop('currency', None)
        instance.update(**validated_data)
        return instance

    def create(self, validated_data):
        return Wallet.objects.create(**validated_data)


class WalletPKField(serializers.PrimaryKeyRelatedField):
    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        serializer = WalletSerializer(value)
        return serializer.data


class TransactionSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    from_user = UserPKField(read_only=True)
    to_user = UserPKField(queryset=User.objects.all())
    amount = serializers.FloatField()
    currency = CurrencyPKField(
        queryset=Currency.objects.all(),
        slug_field='code',
    )
    paid_at = serializers.ReadOnlyField()

    def validate_to_user(self, value):
        user = self.context['request'].user
        if value.id == user.id:
            raise serializers.ValidationError('You cannot send money to yourself.')

        return value

    def validate(self, attrs):
        user = self.context['request'].user
        from_user_wallet = generics.get_object_or_404(Wallet, user=user, currency=attrs['currency'])

        if from_user_wallet.balance < attrs['amount']:
            raise serializers.ValidationError('You\'d have enough money to send.')

        to_user_wallet_qs = Wallet.objects.filter(user=attrs['to_user'], currency=attrs['currency'])
        if not to_user_wallet_qs.exists():
            raise serializers.ValidationError(
                'User that you want to send money doesn\'t have a wallet in given currency'
            )

        return attrs

    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)


class ExchangeCurrencySerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    from_wallet = WalletPKField(queryset=Wallet.objects.all())
    to_wallet = WalletPKField(queryset=Wallet.objects.all())
    from_amount = serializers.FloatField()

    def validate_from_wallet(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError('Source wallet doesn\'t belong to you.')

        return value

    def validate_to_wallet(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError('Target wallet doesn\'t belong to you.')

        return value

    def validate(self, attrs):
        if attrs['from_wallet'].balance < attrs['from_amount']:
            raise serializers.ValidationError('You don\'t have enough money to exchange.')

        rate_qs = ExchangeRate.objects.filter(
            from_currency=attrs['from_wallet'].currency,
            to_currency=attrs['to_wallet'].currency,
        )
        if not rate_qs.exists():
            raise serializers.ValidationError('There is no exchange rate available between those currencies.')

        return attrs
