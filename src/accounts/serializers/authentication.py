from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


class TokenObtainSerializer(serializers.Serializer):
    access = serializers.SerializerMethodField()
    refresh = serializers.SerializerMethodField()

    def get_access(self, obj):
        return str(AccessToken.for_user(obj))

    def get_refresh(self, obj):
        return str(RefreshToken.for_user(obj))
