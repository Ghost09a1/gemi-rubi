from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils.translation import gettext_lazy as _


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "success": False,
            "error": {
                "code": response.status_code,
                "message": str(exc),
                "details": response.data if hasattr(response, "data") else None,
            },
        }

        # Handle specific error types
        if isinstance(exc, ValidationError):
            error_data["error"]["message"] = _("Validation error")
            error_data["error"]["fields"] = exc.message_dict
        elif isinstance(exc, Http404):
            error_data["error"]["message"] = _("Resource not found")

        response.data = error_data

    return response
