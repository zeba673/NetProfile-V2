"""
app/__init__.py — Flask Application Factory
"""
import sqlite3
import os
import pg8000.dbapi
from flask import Flask, g
from config import Config


class PgCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor
        self.description = cursor.description

    def execute(self, sql, params=None):
        # Convert SQLite ? placeholder to PostgreSQL %s
        sql = sql.replace('?', '%s')
        
        # Replace SQLite datetime('now') and date('now')
        sql = sql.replace("datetime('now')", "CURRENT_TIMESTAMP")
        sql = sql.replace("date('now')", "CURRENT_DATE")
        
        if params is not None:
            if not isinstance(params, (tuple, list)):
                params = (params,)
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        return self

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        colnames = [desc[0] for desc in self.cursor.description]
        return dict(zip(colnames, row))

    def fetchall(self):
        rows = self.cursor.fetchall()
        if not rows:
            return []
        colnames = [desc[0] for desc in self.cursor.description]
        return [dict(zip(colnames, r)) for r in rows]

    @property
    def lastrowid(self):
        # Fetch the last inserted ID in the session (standard PostgreSQL function)
        self.cursor.execute("SELECT lastval()")
        row = self.cursor.fetchone()
        return row[0] if row else None


class PgConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        return PgCursorWrapper(self.conn.cursor())

    def execute(self, sql, params=None):
        cursor = self.cursor()
        cursor.execute(sql, params)
        return cursor

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


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
        # Check if environment variables for PostgreSQL are set
        pg_host = os.environ.get('DB_HOST') or os.environ.get('POSTGRES_HOST')
        if pg_host:
            # Connect to PostgreSQL (Supabase)
            db_user = os.environ.get('DB_USER') or os.environ.get('POSTGRES_USER')
            db_pass = os.environ.get('DB_PASSWORD') or os.environ.get('POSTGRES_PASSWORD')
            db_name = os.environ.get('DB_NAME') or os.environ.get('POSTGRES_DATABASE')
            db_port = int(os.environ.get('DB_PORT', 5432))
            
            conn = pg8000.dbapi.connect(
                user=db_user,
                password=db_pass,
                host=pg_host,
                port=db_port,
                database=db_name
            )
            g.db = PgConnectionWrapper(conn)
        else:
            # Fallback to local SQLite database
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
