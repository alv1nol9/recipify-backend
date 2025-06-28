from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
import os

from server.config import Config
from server.models.base import db
from server.controllers.routes import init_routes

# 🔁 Import models to register relationships (REQUIRED!)
from server import models

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)

    init_routes(app)

    with app.app_context():
        db.create_all()

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        return send_from_directory(uploads_dir, filename)

    return app

# 👇 Define app at module level so gunicorn can find it
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
