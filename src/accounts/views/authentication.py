from drf_yasg.utils import swagger_auto_schema

from django.utils.decorators import method_decorator
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from ..serializers.authentication import TokenObtainSerializer


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='[Login] Login with user credentials and receive JWTs for access and refresh.',
    responses={'200': TokenObtainSerializer()},
))
class LoginAPIView(TokenObtainPairView):
    pass


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='[Refresh Token] Refresh JWTs with refresh token.',
    responses={'200': TokenObtainSerializer()},
))
class RefreshTokenAPIView(TokenRefreshView):
    pass
