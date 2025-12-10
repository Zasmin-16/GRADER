from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from .main_routes import main_bp 


db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    # Import blueprints
    from .auth_routes import auth_bp
    from .professor_routes import professor_bp
    from .student_routes import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(professor_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(main_bp)
    # Create DB tables
    with app.app_context():
        db.create_all()

    return app
