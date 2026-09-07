"""Điểm vào WSGI cho server production và cho `flask --app wsgi run`."""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
