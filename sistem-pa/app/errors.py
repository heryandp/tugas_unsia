from flask import current_app


def register_errors(app):
    @app.errorhandler(500)
    def internal_error(error):
        import traceback

        error_details = traceback.format_exc()
        current_app.logger.error(error_details)
        if current_app.config.get("SHOW_TRACEBACK"):
            return f"""
            <h1>Internal Server Error</h1>
            <p>Terjadi kesalahan saat memproses request.</p>
            <details>
              <summary>Detail Error (klik untuk expand)</summary>
              <pre>{error_details}</pre>
            </details>
            <p><a href='/dashboard/input-perkara'>Kembali ke Dashboard</a></p>
            """, 500
        return """
        <h1>Internal Server Error</h1>
        <p>Terjadi kesalahan saat memproses request.</p>
        <p>Silakan coba lagi atau hubungi admin.</p>
        <p><a href='/dashboard/input-perkara'>Kembali ke Dashboard</a></p>
        """, 500

    @app.errorhandler(413)
    def too_large(_e):
        return "<h1>File terlalu besar</h1><p>Maksimal 16MB</p>", 413
