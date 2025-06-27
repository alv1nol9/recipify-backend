from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from server.config import Config
from server.models import db
from server.controllers.routes import init_routes  

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)

    CORS(app)

    with app.app_context():
        db.create_all()

    init_routes(app)  

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
