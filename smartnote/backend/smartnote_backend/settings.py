import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from datetime import timedelta

# Tải các biến môi trường từ file .env
load_dotenv()

# Cấu hình cơ bản của Django
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-xxxxxxxxxxxx")
DEBUG = True
ALLOWED_HOSTS = ["*"]  # Chỉ dùng cho môi trường dev

# --- CẤU HÌNH API AI ---
# Sử dụng biến môi trường để chuyển đổi giữa các nhà cung cấp AI
# Mặc định là Gemini
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")

# Cấu hình cho OpenAI (giữ lại để tham khảo hoặc chuyển đổi sau này)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.7

# Cấu hình cho Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Sử dụng gemini-1.5-flash-001 vì đây là phiên bản ổn định
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-pro-latest")


AUTH_USER_MODEL = 'users.User'

# Hoặc bạn có thể dùng biến môi trường để linh hoạt hơn:
# GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-001")

# --- DANH SÁCH CÁC ỨNG DỤNG ---
INSTALLED_APPS = [
    'users.apps.UserConfig',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "notes",
    "api_mazii",
    "openai_api",
    "ai_content",
    'drf_spectacular',
    'drf_yasg',
    "rest_framework_simplejwt.token_blacklist"
    
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --- CẤU HÌNH KHÁC ---
ROOT_URLCONF = "smartnote_backend.urls"
WSGI_APPLICATION = "smartnote_backend.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'django.template.context_processors.debug',
            ],
        },
    }
]

# --- CƠ SỞ DỮ LIỆU ---
# settings.py
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

load_dotenv(os.path.join(BASE_DIR, ".env"))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    },
    "server": {   # Server DB (smartNote_server_db)
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("SERVER_DB_NAME"),
        "USER": os.getenv("SERVER_DB_USER"),
        "PASSWORD": os.getenv("SERVER_DB_PASSWORD"),
        "HOST": os.getenv("SERVER_DB_HOST"),
        "PORT": os.getenv("SERVER_DB_PORT", "3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    },
}

DATABASE_ROUTERS = ["smartnote_backend.dbrouters.SmartNoteRouter"]

# --- BẢO MẬT MẬT KHẨU ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- QUỐC TẾ HÓA ---
LANGUAGE_CODE = "en-us" 
TIME_ZONE = "Asia/Ho_Chi_Minh" 
USE_I18N = True
USE_TZ = True

# --- CẤU HÌNH REST FRAMEWORK ---
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ]
}

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 2,  # mặc định mỗi trang 2 object
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

INSTALLED_APPS += ["django_extensions"]


REST_FRAMEWORK = {
     "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",  # tuỳ bạn
    ],
    "EXCEPTION_HANDLER": "utils.exception_handler.custom_exception_handler",
}

# Lấy key ký JWT từ biến môi trường, fallback về SECRET_KEY (nên đặt riêng)
JWT_SIGNING_KEY = os.environ.get("JWT_SIGNING_KEY", SECRET_KEY)

# Setting cho Simple JWT
SIMPLE_JWT = {
    "ALGORITHM": "HS256",                 # <-- HS256
    "SIGNING_KEY": JWT_SIGNING_KEY,       # khóa đối xứng để ký & verify
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,        # quay vòng refresh
    "BLACKLIST_AFTER_ROTATION": True,     # và blacklist cái cũ
    "AUTH_HEADER_TYPES": ("Bearer",),     # Authorization: Bearer <token>
    "LEEWAY": 30,  # cho phép lệch giờ 30s
}

# blacklist refresh token sau khi dùng
SIMPLE_JWT = {
    # nếu dùng rotate refresh:
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}



STATIC_URL = "/static/"
