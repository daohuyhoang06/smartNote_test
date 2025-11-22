import requests
import xml.etree.ElementTree as ET
from django.http import JsonResponse, HttpResponse
from .serializers import WordSerializer, KanjiSerializer, ExampleSerializer


class Word:
    word: str
    lang: str
    type: str

    def __init__(self, word, lang='javi', type=None):
        # Khởi tạo các thuộc tính
        self.word = word
        self.lang = lang
        self.type = type
       
    def getWord(self):
        return self.word
    
    def getLang(self):
        return self.lang
    
    def getType(self):
        return self.type


    # def getExample(self):
    #     url = "https://mazii.net/api/search"
    #     response = requests.post(url, json={
    #         'type': 'example',
    #         'dict': self.lang,
    #         'query': self.word,
    #         'limit': 2
    #     }, headers={'Content-Type': 'application/json'})

    #     if response.status_code != 200:
    #         return {"error": "Failed to fetch data from the dictionary API"}
        
    #     exampleData = response.json().get('results', [])
    #     result = {}

    #     if not exampleData:
    #         return {"error": "No data found for the given word"}
        
    #     for i, example in enumerate(exampleData):
    #         result[i] = ExampleSerializer(data = example)
    #         if result[i].is_valid():
    #             result[i] = result[i].validated_data

    #     return result 
    

    def getComment(self, word):
        pass

    def getMeaning(self):
        pass
    

class Kanji(Word):
    def __init__(self, word, lang, type):
        # Khởi tạo các thuộc tính
        super().__init__(word, lang, type)

    def getMeaning(self):
        url = "https://mazii.net/api/search"
        response = requests.post(url, data={
            'dict': self.lang,
            'type': "kanji",
            'query': self.word,
            'limit': '1'
        })
        # Check if the request was successful
        if response.status_code != 200:
            return {"error": "Failed to fetch data from the dictionary API"}

        wordData = response.json().get('results', [])
        # Check if the response contains data
        if not wordData:
            return {"error": "No data found for the given word"}
        
        meaning = KanjiSerializer(data = wordData[0])
        
        if meaning.is_valid():
            meaning = meaning.validated_data
            return meaning
        
        return {}
    
    def getKanjiArt(self):
        try:
            unicode_kanji = unicode_encoding(f'{self.word}')
            url = f'https://data.mazii.net/kanji/0{unicode_kanji}.svg'
            
            # Fetch the SVG data
            response = requests.get(url)
            response.raise_for_status()  
            kanji_art_data = response.text

            # Parse the SVG data
            try:
                # You can use ElementTree to parse XML
                root = ET.fromstring(kanji_art_data)
                # If needed, you can extract specific parts from the SVG data here.
                # For simplicity, we'll return the whole SVG data.
                svg_data = ET.tostring(root, encoding='unicode')
                return svg_data
            except ET.ParseError as e:
                return JsonResponse({'error': 'Error parsing XML', 'details': str(e)}, status=500)

        except requests.RequestException as e:
            return JsonResponse({'error': 'Error fetching art', 'details': str(e)}, status=500)
        

class NonKanji(Word):
    def __init__(self, word, lang, type):
        super().__init__(word, lang, type)

    def getMeaning(self):
        # Xác định limit gốc theo loại từ (API trả về tối đa)
        if all('\u3040' <= ch <= '\u309F' for ch in self.word) or all('\u30A0' <= ch <= '\u30FF' for ch in self.word):
            limit = 4  # Hiragana/Katakana
        else:
            limit = 1  # Kanji

        url = "https://mazii.net/api/search"
        response = requests.post(url, data={
            'dict': self.lang,
            'type': "word",
            'query': self.word,
            'limit': limit,
        })

        if response.status_code != 200:
            return {"error": "Failed to fetch data from the dictionary API"}

        wordData = response.json().get('data', [])

        
        if not wordData:
            return {"error": "No data found for the given word"}

        meanings = []
        for item in wordData:
            serializer = WordSerializer(data=item)
            if serializer.is_valid():
                meaning = serializer.validated_data
                # Lấy ví dụ
                word_obj = NonKanji(meaning['word'], lang='javi', type='word')
                # meaning['examples'] = word_obj.getExample()
                meanings.append(meaning)

        return meanings




def unicode_encoding(word):
    # Get the Unicode code point of the first character
    code_point = ord(word)
    # Convert the code point to a hexadecimal string
    hex_code = hex(code_point)[2:]  # Remove the '0x' prefix
    return hex_code
