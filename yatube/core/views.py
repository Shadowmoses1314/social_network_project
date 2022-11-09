from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    return render(
        request,
        'core/404.html', {'path': request.path}, status=HTTPStatus.NOT_FOUND)


def permission_denied(request, reason=''):
    return render(
        request,
        'core/403csrf.html',
        {'path': request.path}, status=HTTPStatus.FORBIDDEN)


def internal_server_error(request):
    return render(
        request,
        'core/500.html',
        {'path': request.path}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
