from drf_yasg.utils import swagger_auto_schema

from django.utils.decorators import method_decorator
from rest_framework import status, generics, permissions
from rest_framework.response import Response

from ..emails import send_reset_email
from ..models import User
from ..serializers.password import UpdatePasswordSerializer, ResetPasswordSerializer
from ..serializers.registration import EmailSerializer
from ..utils import get_user_uidb64_token


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_summary='[Update Password] Update the password when user knows the old one.',
    responses={'204': ''},
))
class PasswordAPIView(generics.UpdateAPIView):
    serializer_class = UpdatePasswordSerializer

    def get_object(self):
        return self.request.user


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary='[Reset Password] Reset password with token from email.',
    responses={'204': ''},
))
class ResetPasswordAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = get_user_uidb64_token(data['uidb64'], data['token'])
        user.set_password(data['new_password'])
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SendResetEmailAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = EmailSerializer

    @swagger_auto_schema(
        operation_summary='[Send Reset Email] Send email with the link to reset password.',
        responses={'204': ''},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = generics.get_object_or_404(User, email=data['email'])
        send_reset_email(request, user)

        return Response(status=status.HTTP_204_NO_CONTENT)
