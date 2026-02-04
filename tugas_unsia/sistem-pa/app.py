from app import create_app


app = create_app()


if __name__ == "__main__":
    import webbrowser
    from threading import Timer

    def open_browser():
        webbrowser.open("http://127.0.0.1:5000")

    Timer(1.5, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
