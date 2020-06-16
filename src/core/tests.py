def test_response(detail=''):
    return {'detail': detail}


def test_to_non_field_errors(detail):
    return [{
        'key': 'non_field_errors',
        'detail': detail if isinstance(detail, list) else [detail],
    }]


def test_error_response(error=None):
    response = []
    if error is None:
        response = []
    elif isinstance(error, (list, str)):
        response = test_to_non_field_errors(error)
    elif isinstance(error, dict):
        error = {k: v if isinstance(v, list) else [v] for k, v in error.items()}
        response = [{'key': k, 'detail': v} for k, v in error.items()]
    return response
