import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# --- Load biến môi trường từ file .env ---
BASE_DIR = Path(__file__).resolve().parent.parent  # thư mục backend
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)

# --- Lấy API key ---
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ Bạn chưa đặt GEMINI_API_KEY trong file .env hoặc biến môi trường!")

# --- Cấu hình Gemini ---
genai.configure(api_key=API_KEY)

print("📌 Danh sách model khả dụng trong tài khoản của bạn:\n")

try:
    models = genai.list_models()
    for m in models:
        print(f"- {m.name} | methods: {m.supported_generation_methods}")
except Exception as e:
    print("❌ Lỗi khi gọi Gemini API:", e)
