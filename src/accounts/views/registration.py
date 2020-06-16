from drf_yasg.utils import swagger_auto_schema

from django.utils.translation import ugettext as _
from rest_framework import status, exceptions, generics, permissions
from rest_framework.response import Response

from ..emails import send_activation_email
from ..models import User
from ..serializers.authentication import TokenObtainSerializer
from ..serializers.registration import CheckFieldTakenSerializer, EmailSerializer, ActivateAccountSerializer
from ..serializers.users import MeSerializer
from ..utils import get_user_uidb64_token


class RegistrationAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MeSerializer

    @swagger_auto_schema(
        operation_summary='[Register Account] Register a new account.',
        responses={'200': TokenObtainSerializer()}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        send_activation_email(request, instance)

        serializer = TokenObtainSerializer(instance=instance)
        return Response(serializer.data)


class CheckFieldTakenAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CheckFieldTakenSerializer

    @swagger_auto_schema(
        operation_summary='[Check Field Taken] Check if user with given field and its value already exists.',
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class ResendEmailAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = EmailSerializer

    @swagger_auto_schema(
        operation_summary='[Resend Activation Email] Resend account activation email.',
        responses={'204': ''}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        user = generics.get_object_or_404(User, email=email)
        if not user.is_email_verified:
            send_activation_email(request, user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivateAccountAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ActivateAccountSerializer

    @swagger_auto_schema(
        operation_summary='[Activate Account] Activate user account with uidb64 and token from the email link.',
        responses={'204': ''},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        user = get_user_uidb64_token(uidb64, token)

        if not user.is_active:
            raise exceptions.PermissionDenied(_('Your account is deactivated, contact support for more details.'))

        user.is_email_verified = True
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
