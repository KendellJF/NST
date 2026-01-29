import os
from flask import Flask
from flask_migrate import Migrate
from models import db
# import blueprints (adjust names/paths)
# from routes import main_bp
# from Controllers.auth import auth_bp

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Default config
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///instance/app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET=os.environ.get('JWT_SECRET', 'change-me'),
        JWT_ALGORITHM=os.environ.get('JWT_ALGORITHM', 'HS256'),
        JWT_EXP_MINUTES=int(os.environ.get('JWT_EXP_MINUTES', '60')),
        ADMIN_USERNAME=os.environ.get('ADMIN_USERNAME', 'admin'),
        ADMIN_PASSWORD=os.environ.get('ADMIN_PASSWORD', 'password'),
    )

    if test_config is not None:
        app.config.update(test_config)
    else:
        # load the instance config, if it exists
        app.config.from_pyfile('config.py', silent=True)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints (uncomment and adjust)
    # app.register_blueprint(main_bp)
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    # Create DB tables if not present (optional for dev)
    # with app.app_context():
    #     db.create_all()

    return app

# Convenience for running with `python app.py`
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)