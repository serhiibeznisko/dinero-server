from django.utils.translation import ugettext as _
from rest_framework import serializers

from .models import User


class UserUniqueFieldsValidator(object):
    def __init__(self, fields):
        self.fields = fields
        self.request = None

    def __call__(self, attrs):
        for field in self.fields:
            value = attrs.get(field, serializers.empty)
            if value == serializers.empty:
                continue
            qs = User.all.filter(**{field: value})
            if self.request and self.request.user:
                qs = qs.exclude(id=self.request.user.id)
            if qs.exists():
                field_pretty = field.replace('_', ' ').capitalize()
                raise serializers.ValidationError({
                    field: _('%(field)s is already taken.') % {'field': field_pretty}
                })

        return attrs

    def set_context(self, serializer_field):
        self.request = serializer_field.context.get('request')
