import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("prepora.exceptions")


class PreporaDomainException(Exception):
    def __init__(self, message, code="BUSINESS_RULE_VIOLATION", status_code=400, details=None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)


def custom_exception_handler(exc, context):
    """
    RFC 7807 compliant global exception handler converting DRF and domain exceptions
    into standardized JSON error envelopes.
    """
    response = exception_handler(exc, context)
    request = context.get("request")
    request_id = getattr(request, "request_id", "N/A") if request else "N/A"

    if isinstance(exc, PreporaDomainException):
        error_payload = {
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "status_code": exc.status_code,
                "details": exc.details,
                "request_id": request_id,
            },
        }
        return Response(error_payload, status=exc.status_code)

    if response is not None:
        custom_details = []
        if isinstance(response.data, dict):
            for field, errors in response.data.items():
                msg = errors[0] if isinstance(errors, list) else str(errors)
                custom_details.append({"field": field, "message": msg})
        elif isinstance(response.data, list):
            custom_details = [{"message": str(e)} for e in response.data]

        error_payload = {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR" if response.status_code == 400 else "API_ERROR",
                "message": "Request validation or execution failed.",
                "status_code": response.status_code,
                "details": custom_details,
                "request_id": request_id,
            },
        }
        response.data = error_payload
        return response

    # Unhandled 500 Server Errors
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return Response(
        {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again later.",
                "status_code": 500,
                "details": [],
                "request_id": request_id,
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
