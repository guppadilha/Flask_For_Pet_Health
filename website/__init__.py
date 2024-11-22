from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Importe o Migrate

db = SQLAlchemy()
migrate = Migrate()  # Inicialize o Migrate

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'PIMWEBSITE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)  # Inicialize o Migrate

    # Registrar o Blueprint
    from .routes import routes  # Importe seu Blueprint
    app.register_blueprint(routes)

    return app
