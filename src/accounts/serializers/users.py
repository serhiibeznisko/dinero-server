from django.contrib.auth import password_validation
from rest_framework import serializers

from ..models import User
from ..validators import UserUniqueFieldsValidator


class UseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'name',
        )


class MeSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    is_staff = serializers.ReadOnlyField()
    is_superuser = serializers.ReadOnlyField()
    email = serializers.EmailField()
    name = serializers.CharField(max_length=128)
    password = serializers.CharField(write_only=True, validators=[password_validation.validate_password])

    class Meta:
        validators = [
            UserUniqueFieldsValidator(['email'])
        ]

    def update(self, instance, validated_data):
        validated_data.pop('email', None)  # email can't be changed by default
        validated_data.pop('password', None)
        instance.update(**validated_data)
        return instance

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        return User.objects.create_user(email, password, **validated_data)


class UserPKField(serializers.PrimaryKeyRelatedField):
    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        serializer = UseSerializer(value)
        return serializer.data
