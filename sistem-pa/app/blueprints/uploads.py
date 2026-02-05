import os

from flask import Blueprint, current_app, send_file, abort


bp = Blueprint("uploads", __name__)


@bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve uploaded files from the uploads directory."""
    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        
        # Construct absolute path
        file_path = os.path.abspath(os.path.join(upload_folder, filename))
        upload_folder_abs = os.path.abspath(upload_folder)
        
        # Security: prevent directory traversal
        if not file_path.startswith(upload_folder_abs):
            current_app.logger.warning(f"Directory traversal attempt: {filename}")
            abort(404)
        
        # Check if file exists
        if not os.path.isfile(file_path):
            current_app.logger.warning(f"File not found: {file_path}")
            abort(404)
        
        # Serve the file
        return send_file(file_path)
        
    except Exception as e:
        current_app.logger.error(f"Error serving file {filename}: {e}", exc_info=True)
        abort(404)
