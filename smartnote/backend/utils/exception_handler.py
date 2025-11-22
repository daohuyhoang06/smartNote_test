from rest_framework.views import exception_handler as drf_handler
from rest_framework import status as http_status
from .api_response import respond
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

def custom_exception_handler(exc, context):
    resp = drf_handler(exc, context)
    if resp is not None:
        data = resp.data
        # Nếu là lỗi validate (400) và có chi tiết field -> đưa vào errors
        if resp.status_code == 400 and isinstance(data, (dict, list)):
            return Response({
                "success": False,
                "message": "Validation error",
                "data": {},
                "errors": data,     # <--- QUAN TRỌNG
            }, status=resp.status_code, headers=resp.headers)

        # Các lỗi khác giữ như cũ
        if isinstance(data, dict) and "detail" in data:
            msg = str(data["detail"])
        elif isinstance(data, (dict, list)):
            msg = "Error"
        else:
            msg = str(data)
        return respond(success=False, data={}, message=msg,
                       status=resp.status_code, headers=resp.headers)

    # Lỗi không qua DRF
    return respond(success=False, data={}, message="Internal Server Error",
                   status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)
