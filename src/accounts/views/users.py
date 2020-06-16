from drf_yasg.utils import swagger_auto_schema

from django.utils.decorators import method_decorator
from rest_framework import generics

from ..serializers.users import MeSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary='[My Account] Get own user account information.',
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary='[My Account Update] Perform full update on the account information.',
))
@method_decorator(name='patch', decorator=swagger_auto_schema(
    operation_summary='[My Account Update] Perform partial update on the account information.',
))
class MeAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user
