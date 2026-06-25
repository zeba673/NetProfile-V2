"""
app/__init__.py — Flask Application Factory
"""
import sqlite3
import os
from flask import Flask, g
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)

    # Registrar blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.abogado import abogado_bp
    from app.blueprints.secretaria import secretaria_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(abogado_bp, url_prefix='/abogado')
    app.register_blueprint(secretaria_bp, url_prefix='/secretaria')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Ruta raíz
    from flask import redirect, url_for
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app


def get_db():
    """Obtiene la conexión a la base de datos para el contexto actual."""
    from flask import current_app
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
