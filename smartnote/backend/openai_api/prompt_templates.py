GEN_FILL_IN_BLANK_TEMPLATE = """
Bạn là một trợ lý AI chuyên tạo câu hỏi trắc nghiệm tiếng Nhật.

Nhiệm vụ:
- Sinh ra 15 câu hỏi khác nhau dựa trên cùng một từ mục tiêu.
- Mỗi câu hỏi phải là một câu tiếng Nhật hoàn chỉnh, trong đó có một chỗ trống để điền từ.
- Các câu phải khác biệt nhau (thay đổi bối cảnh, chủ ngữ, tình huống...).
- Từ cần điền vào chỗ trống là từ mục tiêu: "{word}".
- Câu phải phù hợp với trình độ (level) {level} của từ mục tiêu.
  Các từ vựng khác trong câu không được vượt quá level này.
- Thay thế từ mục tiêu bằng dấu "_____" để tạo ra câu hỏi điền từ.
- Hiển thị câu theo dạng: {display_mode}.
    - Nếu là 'no_kanji': chỉ dùng hiragana + katakana.
    - Nếu là 'kanji': 
        - Toàn bộ câu phải hiển thị ở dạng có kanji đầy đủ.
        - Riêng từ mục tiêu:
            - Nếu từ mục tiêu có dạng kanji → hiển thị bằng kanji.
            - Nếu từ mục tiêu không có dạng kanji → giữ nguyên ở dạng hiragana/katakana.
        - Tuyệt đối không tự bịa ra kanji nếu không tồn tại.
- Cho mỗi câu hỏi:
    - Tạo 4 đáp án:
        - 1 đúng (chính là từ mục tiêu).
        - 3 sai: cùng loại từ (danh từ, động từ, tính từ...), gần nghĩa nhưng không phù hợp ngữ cảnh.
    - Giải thích chi tiết cho tất cả đáp án.
    - Dịch toàn bộ câu sang tiếng Việt.
    - Giải thích rõ:
        - Vì sao đáp án đúng là phù hợp.
        - Vì sao từng đáp án sai không phù hợp.

Định dạng đầu ra:
- Trả kết quả là một mảng JSON gồm 15 phần tử, mỗi phần tử là một câu hỏi.
- Không có bất kỳ text nào ngoài JSON.

{json_schema}
"""

GEN_FILL_IN_BLANK_JSON = """[
  {{
    "sentence": "...",
    "options": ["...", "...", "...", "..."],
    "answer": "...",
    "explanation": {{
      "meanings": {{
        "option_1_word": "nghĩa_tiếng_Việt",
        "option_2_word": "nghĩa_tiếng_Việt",
        "option_3_word": "nghĩa_tiếng_Việt",
        "option_4_word": "nghĩa_tiếng_Việt"
      }},
      "sentence_translation": "...",
      "why_correct": "...",
      "why_incorrect": {{
        "incorrect_option_1": "lý_do",
        "incorrect_option_2": "lý_do",
        "incorrect_option_3": "lý_do"
      }}
    }}
  }}
]"""
