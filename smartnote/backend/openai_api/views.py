from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import generate_fill_in_blank
from rest_framework.permissions import AllowAny
from drf_spectacular.openapi import AutoSchema

class GenerateFillInBlankView(APIView):

     # Không dùng bất kỳ cơ chế xác thực nào
    authentication_classes = []             # 👈 tắt auth
    schema = AutoSchema()
    permission_classes = [AllowAny]         # 👈 cho phép truy cập tự do
    
    """
    Tạo nhiều câu hỏi điền từ (mặc định 15 câu).
    - Phương thức POST: Nhận tham số từ body.
    - Phương thức GET: Nhận tham số từ query string.

    Ví dụ:
    POST /api/gemini/gen_fill_blank
    GET /api/gemini/gen_fill_blank?word=勉強&level=N4&display_mode=kanji
    """
    def _handle_request(self, word, level, display_mode, count):
        if not word:
            return Response({"error": "Thiếu tham số 'word'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = generate_fill_in_blank(word, level, display_mode, count=count)
            return Response({"results": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        word = request.data.get("word")
        level = request.data.get("level", "N5")
        display_mode = request.data.get("display_mode", "kanji")
        count = int(request.data.get("count", 15))  # cho phép override số câu nếu cần
        return self._handle_request(word, level, display_mode, count)

    def get(self, request):
        word = request.query_params.get("word")
        level = request.query_params.get("level", "N5")
        display_mode = request.query_params.get("display_mode", "kanji")
        count = int(request.query_params.get("count", 15))  # cho phép override số câu nếu cần
        return self._handle_request(word, level, display_mode, count)
