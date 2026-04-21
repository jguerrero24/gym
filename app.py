import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from config.db import get_db
from models.user import seed
from routes import register_routes

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="")
    app.secret_key = os.environ.get("SECRET_KEY", "gymlog-dev-secret-change-me")

    is_prod = os.environ.get("FLASK_ENV") == "production"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "None" if is_prod else "Lax"
    app.config["SESSION_COOKIE_SECURE"]   = is_prod
    app.config["SESSION_COOKIE_NAME"]     = "gymlog_session"

    # Trust Render's proxy headers (HTTPS)
    if is_prod:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    CORS(app, supports_credentials=True,
         origins=os.environ.get("CORS_ORIGINS", "*").split(","))

    register_routes(app)

    # Serve frontend
    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def catch_all(path):
        full = os.path.join(app.static_folder, path)
        if os.path.isfile(full):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    # Initialize DB + seed on first boot
    with app.app_context():
        try:
            get_db()
            seed()
            print("✅  MongoDB conectado y seed completado")
        except Exception as e:
            print(f"⚠️  Error conectando a MongoDB: {e}")

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_ENV") != "production")

