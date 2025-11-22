from rest_framework.response import Response
from rest_framework import status as http_status

def respond(*, success: bool, data=None, message="OK", status=http_status.HTTP_200_OK, **kwargs):
    payload = {
        "success": bool(success),
        "message": message or "",
        "data": (data if success and data is not None else {}),
    }
    return Response(payload, status=status, **kwargs)

def ok(data=None, message="OK", status=http_status.HTTP_200_OK, **kwargs):
    return respond(success=True, data=data, message=message, status=status, **kwargs)

def fail(message="Bad Request", status=http_status.HTTP_400_BAD_REQUEST, **kwargs):
    return respond(success=False, data={}, message=message, status=status, **kwargs)

def fail_errors(errors, message="Validation error", status=http_status.HTTP_400_BAD_REQUEST, **kwargs):
    payload = {
        "success": False,
        "message": message,
        "data": {},
        "errors": errors,          # chi tiết lỗi
    }
    return Response(payload, status=status, **kwargs)  # <--- PHẢI có return
