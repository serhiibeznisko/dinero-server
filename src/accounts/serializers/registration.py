from rest_framework import serializers

from ..models import User


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ActivateAccountSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()


class CheckFieldTakenSerializer(serializers.Serializer):
    taken = serializers.ReadOnlyField()
    field = serializers.ChoiceField(choices=['email'], write_only=True)
    value = serializers.CharField(write_only=True)

    def validate(self, attrs):
        taken = User.all.filter(**{attrs['field']: attrs['value']}).exists()
        return {'taken': taken}
