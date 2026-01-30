import os
import sys
import traceback
from flask import Flask
from flask_migrate import Migrate
from models import db


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration (override with env or instance/config.py)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(app.instance_path, "app.db")}'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET=os.environ.get('JWT_SECRET', 'change-me'),
        JWT_ALGORITHM=os.environ.get('JWT_ALGORITHM', 'HS256'),
        JWT_EXP_MINUTES=int(os.environ.get('JWT_EXP_MINUTES', '60')),
        ADMIN_USERNAME=os.environ.get('ADMIN_USERNAME', 'admin'),
        ADMIN_PASSWORD=os.environ.get('ADMIN_PASSWORD', 'password'),
        CLEAR_DB_PASSWORD=os.environ.get('CLEAR_DB_PASSWORD', 'delete-all-data'),
        INITIAL_CSV_PATH=os.environ.get('INITIAL_CSV_PATH', 'data/guests.csv'),
        INITIAL_CSV_ON_STARTUP=os.environ.get('INITIAL_CSV_ON_STARTUP', '0') in ('1', 'true', 'yes'),
    )

    if test_config is not None:
        app.config.update(test_config)
    else:
        app.config.from_pyfile('config.py', silent=True)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints if available
    try:
        from routes import main_bp, admin_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')
    except Exception:
        # Routes may not be present during early development/testing
        pass

    # Create DB tables and optionally import initial CSV on startup
    with app.app_context():
        db.create_all()

        csv_path = app.config.get('INITIAL_CSV_PATH')
        if app.config.get('INITIAL_CSV_ON_STARTUP') and csv_path and os.path.exists(csv_path):
            try:
                from scripts.import_initial_csv import import_csv

                import_csv(csv_path)
            except Exception:
                # Do not prevent app from starting if import fails; log to stderr
                traceback.print_exc(file=sys.stderr)

    return app


if __name__ == '__main__':
    app = create_app()
    debug_flag = os.environ.get('FLASK_DEBUG', '0') in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=debug_flag)