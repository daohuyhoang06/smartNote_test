import os
import json
import random
import logging
import google.generativeai as genai
from django.conf import settings
from google.api_core.exceptions import GoogleAPIError, InvalidArgument

logger = logging.getLogger(__name__)

from .prompt_templates import GEN_FILL_IN_BLANK_JSON, GEN_FILL_IN_BLANK_TEMPLATE

# --- MOCK DATA ---
MOCK_VOCAB_BY_LEVEL = {
    "N5": ["勉強", "運動", "料理", "遊び", "読書", "散歩"],
    "N4": ["勉強", "運動", "料理", "遊び", "読書", "散歩", "仕事", "旅行"],
    "N3": ["勉強", "運動", "料理", "遊び", "読書", "散歩", "仕事", "旅行", "買い物"],
}

MOCK_SENTENCE_TEMPLATES = [
    "私は毎日_____をします。",
    "昨日、_____をしました。",
    "週末は_____が好きです。",
    "毎朝_____をしています。"
]

MOCK_MEANINGS = {
    "勉強": "Học tập",
    "運動": "Vận động / tập thể dục",
    "料理": "Nấu ăn",
    "遊び": "Chơi đùa",
    "読書": "Đọc sách",
    "散歩": "Đi dạo",
    "仕事": "Công việc",
    "旅行": "Du lịch",
    "買い物": "Mua sắm"
}


# --- FUNCTIONS ---
def generate_fill_in_blank(word: str, level: str = "N5", display_mode: str = "kanji", count: int = 15):
    """
    Sinh count câu trắc nghiệm đục lỗ dựa trên từ vựng, sử dụng Gemini API.
    - Nếu AI_PROVIDER="mock"   → trả về list count câu giả lập
    - Nếu AI_PROVIDER="gemini" → gọi API Gemini thật, trả về list count câu
    """
    ai_provider = getattr(settings, "AI_PROVIDER", "gemini")

    # --- MOCK ---
    if ai_provider == "mock":
        results = []
        vocab_list = MOCK_VOCAB_BY_LEVEL.get(level, MOCK_VOCAB_BY_LEVEL["N5"])
        for _ in range(count):
            wrong_options = random.sample([w for w in vocab_list if w != word], 3)
            options = [word] + wrong_options
            random.shuffle(options)

            sentence_template = random.choice(MOCK_SENTENCE_TEMPLATES)

            meanings = {opt: MOCK_MEANINGS.get(opt, f"Nghĩa giả lập của {opt}") for opt in options}

            why_correct = f"Từ '{word}' phù hợp nhất với ngữ cảnh của câu."
            why_incorrect = {
                opt: f"Từ '{opt}' nghe hợp lý nhưng không phù hợp trong ngữ cảnh này."
                for opt in options if opt != word
            }

            results.append({
                "sentence": sentence_template,
                "options": options,
                "answer": word,
                "explanation": {
                    "meanings": meanings,
                    "sentence_translation": "Đây là bản dịch giả lập của câu.",
                    "why_correct": why_correct,
                    "why_incorrect": why_incorrect
                }
            })
        return results

    # --- GEMINI API THẬT ---
    api_key = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    if not api_key:
        raise ValueError("Bạn chưa đặt GEMINI_API_KEY trong biến môi trường hoặc settings.py.")

    genai.configure(api_key=api_key)

    prompt = GEN_FILL_IN_BLANK_TEMPLATE.format(
        word=word,
        level=level,
        display_mode=display_mode,
        json_schema=GEN_FILL_IN_BLANK_JSON,
        count=count,
    )

    model = genai.GenerativeModel(
        model_name=getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash-001"),
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=getattr(settings, "GEMINI_TEMPERATURE", 0.7),
            )
        )

        # Kiểm tra đầu ra
        if not response.parts or not response.text:
            logger.error(f"Gemini trả về rỗng: {response}")
            return {"error": "Gemini trả về rỗng", "raw": str(response)}

        content = response.text
        try:
            start_index = content.find("[")  # kỳ vọng JSON list []
            end_index = content.rfind("]")
            if start_index == -1 or end_index == -1:
                raise ValueError("Kết quả không chứa JSON list hợp lệ")

            json_str = content[start_index:end_index + 1]
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError):
            logger.error(f"Gemini trả JSON lỗi: {content}")
            return {"error": "Gemini trả kết quả không phải JSON list", "raw": content}

    except InvalidArgument as e:
        logger.error(f"Lỗi tham số API Gemini: {str(e)}")
        return {"error": str(e)}
    except GoogleAPIError as e:
        logger.error(f"Lỗi gọi Gemini API: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Lỗi không xác định: {str(e)}")
        return {"error": str(e)}
