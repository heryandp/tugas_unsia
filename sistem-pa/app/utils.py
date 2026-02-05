import os
import sys

from flask import current_app


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def allowed_file(filename):
    if not filename:
        return False
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", set())
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def get_file_size(file_obj):
    try:
        stream = file_obj.stream
        pos = stream.tell()
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(pos)
        return size
    except Exception:
        return None


def max_upload_bytes(file_obj, default_mb=2, pdf_mb=5):
    filename = getattr(file_obj, "filename", "") or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "pdf":
        return pdf_mb * 1024 * 1024
    return default_mb * 1024 * 1024


def validate_upload(file_obj, max_bytes=None, require_allowed=True):
    if not file_obj or not file_obj.filename:
        return True, None
    if require_allowed and not allowed_file(file_obj.filename):
        return False, "Tipe file tidak diizinkan."
    if max_bytes:
        size = get_file_size(file_obj)
        if size is not None and size > max_bytes:
            return False, f"Ukuran file maksimal {max_bytes // (1024 * 1024)} MB."
    return True, None


def get_default_logo():
    try:
        logo_path = resource_path("logo_pa_ikn.ico")
        if os.path.exists(logo_path):
            import base64

            with open(logo_path, "rb") as f:
                logo_data = f.read()
            return "data:image/x-icon;base64," + base64.b64encode(logo_data).decode("utf-8")
    except Exception:
        pass
    return "https://upload.wikimedia.org/wikipedia/commons/4/49/Mahkamah_Agung_insignia.svg"


def sanitize_text(value, max_len=2000):
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    value = value.replace("\x00", "")
    if max_len:
        value = value[:max_len]
    return value.strip()
