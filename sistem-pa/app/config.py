import os
import sys


class Config:
    SECRET_KEY = "rahasia_super_admin_ikn_2025_mantap"

    # Resolve base dir for .exe and script
    if getattr(sys, "frozen", False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.abspath(".")

    DATABASE = os.path.join(BASE_DIR, "perkara.db")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "ico"}

    API_TITLE = "Sistem Informasi PA IKN API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/docs"
    OPENAPI_JSON_PATH = "openapi.json"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5"

    # Security
    SHOW_TRACEBACK = False
    CSP_DEFAULT_SRC = "'self'"
    CSP_IMG_SRC = "'self' data: https:"
    CSP_STYLE_SRC = "'self' https: 'unsafe-inline'"
    CSP_SCRIPT_SRC = "'self' https: 'unsafe-inline'"
    CSP_FONT_SRC = "'self' https: data:"
    CSP_CONNECT_SRC = "'self' ws: wss: https:"
