"""
app/blueprints/auth/routes.py — Autenticación con bcrypt
"""
import bcrypt
from flask import (
    render_template, request, redirect, url_for,
    session, flash, current_app
)
from app.blueprints.auth import auth_bp
from app import get_db


def login_required(f):
    """Decorador que verifica sesión activa."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Decorador que verifica el rol del usuario."""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            if session.get('rol') not in roles:
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated
    return decorator


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return _redirect_by_role()

    error = None
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '')

        if not usuario or not password:
            error = 'Por favor completá todos los campos.'
        else:
            db = get_db()
            user = db.execute(
                "SELECT * FROM usuarios WHERE usuario = ?", (usuario,)
            ).fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                session.clear()
                session['user_id'] = user['id']
                session['usuario'] = user['usuario']
                session['nombre_completo'] = user['nombre_completo']
                session['rol'] = user['rol']
                return _redirect_by_role()
            else:
                error = 'Usuario o contraseña incorrectos.'

    return render_template('login.html', error=error)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def _redirect_by_role():
    rol = session.get('rol')
    if rol == 'abogado':
        return redirect(url_for('abogado.dashboard'))
    elif rol == 'secretaria':
        return redirect(url_for('secretaria.dashboard'))
    return redirect(url_for('auth.login'))
