import os

from flask import Blueprint, current_app, send_from_directory


bp = Blueprint("uploads", __name__)


@bp.route("/uploads/<filename>")
def uploaded_file(filename):
    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, filename)
        if not os.path.exists(file_path):
            current_app.logger.warning(f"File tidak ditemukan: {file_path}")
            return "File not found", 404
        return send_from_directory(upload_folder, filename)
    except Exception as e:
        current_app.logger.error(f"Error loading file {filename}: {e}")
        return "File not found", 404
