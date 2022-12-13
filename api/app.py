from models import db
from flask import Flask
from flask_migrate import Migrate
from routes.user import user_pages
from flask_cors import CORS
from flask_jwt_extended import JWTManager


def create_app():
    app = Flask(__name__)

    cors = CORS(app)
    # app.config.from_object('config.Config')
    # app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
    # from config import MongodbConfig
    # app.config.from_object(MongodbConfig)
    from config import Config
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    app.register_blueprint(user_pages, url_prefix='/api/users')
    jwt = JWTManager(app)
    return app
