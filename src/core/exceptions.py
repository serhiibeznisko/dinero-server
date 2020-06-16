import json

from django.conf import settings
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def append_errors_to_dict_array(arr, key, errors):
    for i, item in enumerate(arr):
        if item['key'] == key:
            arr[i]['detail'] += errors
            break
    else:
        arr.append({
            'key': key,
            'detail': errors,
        })


def unpack_serialization_errors(errors, field=None):
    """ Unpack nested serialization errors to list of objects with 'key' and 'detail' attributes. """
    unpacked_errors = []

    if isinstance(errors, dict):
        for field, items in errors.items():
            item_errors = unpack_serialization_errors(items, field=field)
            for error in item_errors:
                append_errors_to_dict_array(unpacked_errors, error['key'], error['detail'])

    elif isinstance(errors, list):
        for item in errors:
            item_errors = unpack_serialization_errors(item, field=field)
            for error in item_errors:
                append_errors_to_dict_array(unpacked_errors, error['key'], error['detail'])

    elif isinstance(errors, str):
        append_errors_to_dict_array(unpacked_errors, field, [errors])

    return unpacked_errors


def unpack_errors(errors):
    if isinstance(errors, list):
        return errors

    try:
        return [str(errors['detail'])]
    except KeyError:
        pass

    return [str(error) for field, error in errors.items()]


def to_non_field_errors(detail):
    if isinstance(detail, str):
        detail = [detail]
    return [{
        'key': 'non_field_errors',
        'detail': detail,
    }]


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    is_serialization_error = isinstance(exc, ValidationError)

    # response is None if there is unhandled non-rest exception
    if not response:
        if settings.DEBUG:
            raise exc

        response = Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = to_non_field_errors('Internal Server Error')
    elif isinstance(exc, Http404):
        data = to_non_field_errors([str(exc)])
    elif is_serialization_error:
        errors_str = json.dumps(response.data)
        data_json = json.loads(errors_str)
        data = unpack_serialization_errors(data_json)
    else:
        detail = unpack_errors(response.data)
        data = to_non_field_errors(detail)

    response.data = data
    return response
