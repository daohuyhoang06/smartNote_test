import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import get_random_exercises
from .serializers import ExerciseSerializer
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import AutoSchema

logger = logging.getLogger(__name__)


class ExerciseView(APIView):
     # Không dùng bất kỳ cơ chế xác thực nào
    authentication_classes = []             # 👈 tắt auth
    schema = AutoSchema()
    permission_classes = [AllowAny]  
    """
    Endpoint: /api/ai/exercise/?word=勉強&display_mode=kanji
    Trả về 1 câu ngẫu nhiên duy nhất
    """
    def get(self, request):
        word = request.query_params.get("word")
        if not word:
            return Response({"error": "Thiếu tham số 'word'"},
                            status=status.HTTP_400_BAD_REQUEST)

        level = request.query_params.get("level", "N5")
        display_mode = request.query_params.get("display_mode", "kanji")
        try:
            count = int(request.query_params.get("count", 15))
        except ValueError:
            return Response({"error": "Tham số 'count' phải là số nguyên"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            exercise = get_random_exercises(word, level, display_mode, count)
            if not exercise:
                return Response({"error": "Không tìm thấy hoặc sinh câu thất bại"},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = ExerciseSerializer(exercise)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("Lỗi khi xử lý ExerciseView")
            return Response({"error": "Đã xảy ra lỗi phía server"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
