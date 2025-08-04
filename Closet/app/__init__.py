from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

# Import Config from its file
from config import Config # This import is correct

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class) # This loads the config, including DATABASE_URL

    # The error occurs HERE because app.config['SQLALCHEMY_DATABASE_URI'] is invalid
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import routes
    app.register_blueprint(routes.bp)

    return app