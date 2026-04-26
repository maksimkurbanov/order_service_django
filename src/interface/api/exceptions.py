from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

from src.application.exceptions import InsufficientStockError, NotFoundError


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, try again later."


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, InsufficientStockError):
            data = {"detail": exc.message}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc, NotFoundError):
            return Response({"detail": exc.message}, status=status.HTTP_404_NOT_FOUND)
    return response
