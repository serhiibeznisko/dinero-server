from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator

from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.http import HttpRequest
from rest_framework.request import Request

from core.exceptions import to_non_field_errors
from core.utils import response_ok

try:
    JWT_PREFIX = settings.JWT_AUTH['JWT_AUTH_HEADER_PREFIX']
except (KeyError, AttributeError):
    JWT_PREFIX = 'JWT'

header_fields = [
    openapi.Parameter('Accept-Language', in_=openapi.IN_HEADER, type=openapi.TYPE_STRING, default='en'),
]

header_fields_auth = [
    openapi.Parameter('Authorization', in_=openapi.IN_HEADER, type=openapi.TYPE_STRING, default=f'{JWT_PREFIX} Token'),
]

query_fields_pagination = [
    openapi.Parameter('limit', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=10),
    openapi.Parameter('offset', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=0),
]


def response_docs_ok(detail=''):
    # swagger only accepts string as a response option
    return str(response_ok(detail))


def response_docs_error(error=None):
    response = []
    if error is None:
        response = []
    elif isinstance(error, (list, str)):
        response = to_non_field_errors(error)
    elif isinstance(error, dict):
        response = [
            {'key': k, 'detail': v}
            for k, v in error.items()
        ]
    return str(response)


def is_auth_param(value):
    return value['name'] == 'Authorization' and value['in'] == 'header'


def not_auth_param(value):
    return not is_auth_param(value)


class MyOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    """ Override default OpenAPISchemaGenerator to add or delete Authentication header
    in manual_parameters based on permission classes for each of project view. """

    def get_overrides(self, view, method):
        overrides = super().get_overrides(view, method)
        manual_parameters = overrides.get('manual_parameters', header_fields)

        anon_request = Request(HttpRequest())
        anon_request.user = AnonymousUser()
        anon_request.method = method
        include_token = not all([
            permission_class().has_permission(anon_request, view)
            for permission_class in view.permission_classes
        ])
        auth_param_found = any([is_auth_param(parameter) for parameter in manual_parameters])

        if include_token and not auth_param_found:
            manual_parameters += header_fields_auth

        if not include_token:
            manual_parameters = list(filter(not_auth_param, manual_parameters))

        overrides['manual_parameters'] = manual_parameters
        return overrides
