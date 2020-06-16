from django.db import connection


class QueryCountDebugMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        total_time = 0
        for query in connection.queries:
            query_time = query.get('time')
            if query_time is None:
                query_time = query.get('duration', 0)
            total_time += float(query_time)

        print(f'{len(connection.queries)} queries run, total {round(total_time, 3)} seconds')
        return response


class NoIndexMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Robots-Tag'] = 'noindex'
        return response
