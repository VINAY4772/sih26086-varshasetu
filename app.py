import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from config import Config
from backend.routes.api import api_bp
from database.initialise import initialise_database

def create_app(test_config=None) -> Flask:
    app = Flask(__name__, static_folder=str(Config.FRONTEND_DIR))
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    # Enable CORS
    CORS(app)

    # Register API blueprint
    app.register_blueprint(api_bp)

    # Serve Single Page Application & Static Assets
    @app.route("/")
    @app.route("/app/")
    def serve_index():
        return send_from_directory(Config.FRONTEND_DIR, "index.html")

    @app.route("/<path:path>")
    def serve_static(path):
        target = Config.FRONTEND_DIR / path
        if target.exists():
            return send_from_directory(Config.FRONTEND_DIR, path)
        return send_from_directory(Config.FRONTEND_DIR, "index.html")

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error."}), 500

    return app

app = create_app()

if __name__ == "__main__":
    # Ensure database is initialised
    initialise_database()

    port = int(os.environ.get("PORT", 5000))
    print(f"🌾 VarshaSetu Flask Server listening on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
