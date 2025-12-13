from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .utils import NonKanji, Kanji, Word
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from drf_spectacular.utils import extend_schema


def limit_examples(data, limit=2):
    """Giới hạn mỗi âm đọc tối đa limit ví dụ"""
    if not data:
        return data
 
    if isinstance(data, dict):
        limited_data = {}
        for reading, examples in data.items():
            formatted_examples = [
                f"{ex['w']} ({ex['p']}) {ex['m']}"
                for ex in examples[:limit]
            ]
            limited_data[reading] = formatted_examples
        return limited_data

    elif isinstance(data, list):
        return [
              f"{ex['w']} ({ex['p']}) {ex['m']}"
            for ex in data[:limit]
        ]

@extend_schema(exclude=True)
@api_view(["GET"])
@permission_classes([AllowAny])
def searchWord(request, pk):   # pk sẽ nhận "不完全" / "しぜん" ...
    try:
        word = NonKanji(pk, 'javi', 'word')
        results = word.getMeaning()           # phải trả về dict/list JSON-serializable
        if not results:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(results, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(exclude=True)
@api_view(['GET'])
@permission_classes([AllowAny])        # <-- đặt ở decorator
@authentication_classes([])            # <-- bỏ parse JWT
def searchKanji(request, pk):
    
    if request.method == 'GET':
        results = []
        for char in pk:
            kanji = Kanji(char, 'javi', 'kanji')
            meaning_data = kanji.getMeaning()  # Lấy dữ liệu đầy đủ, bao gồm example_on & example_kun
            
            # Giới hạn các ví dụ
            if meaning_data.get('examples'):
                meaning_data['examples'] = limit_examples(meaning_data['examples'])
            if meaning_data.get('example_on'):
                meaning_data['example_on'] = limit_examples(meaning_data['example_on'])
            if meaning_data.get('example_kun'):
                meaning_data['example_kun'] = limit_examples(meaning_data['example_kun'])

            kanjiArt = kanji.getKanjiArt()
            
            results.append ({
                'kanji': char,
                'meaning': meaning_data,
                'kanjiArt': kanjiArt
            })
        return Response(results)
    
