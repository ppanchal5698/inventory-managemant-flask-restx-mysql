# Flask Application Entry Point

from app import create_app

app = create_app()


def main():
    """Run the Flask application."""
    app.run(debug=True, host='0.0.0.0', port=5001)


if __name__ == "__main__":
    main()
