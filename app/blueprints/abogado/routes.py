"""
app/blueprints/abogado/routes.py — Rutas del panel del Abogado
"""
from flask import render_template, session, redirect, url_for
from app.blueprints.abogado import abogado_bp
from app.blueprints.auth.routes import login_required, role_required
from app import get_db


@abogado_bp.route('/dashboard')
@role_required('abogado')
def dashboard():
    db = get_db()
    user_id = session['user_id']

    # KPIs iniciales para renderizado SSR
    casos_activos = db.execute(
        "SELECT COUNT(*) as c FROM casos WHERE abogado_id=? AND estado IN ('activo','en_curso')",
        (user_id,)
    ).fetchone()['c']

    ingresos_total = db.execute(
        "SELECT COALESCE(SUM(monto),0) as t FROM movimientos_caja WHERE tipo='ingreso' AND usuario_id=?",
        (user_id,)
    ).fetchone()['t']

    audiencias_proximas = db.execute(
        """SELECT aa.*, c.expediente FROM audiencias_agenda aa
           LEFT JOIN casos c ON aa.caso_id = c.id
           WHERE (c.abogado_id=? OR aa.caso_id IS NULL) AND aa.estado != 'cancelada'
           ORDER BY aa.fecha_hora LIMIT 5""",
        (user_id,)
    ).fetchall()

    casos_criticos = db.execute(
        """SELECT c.*, cl.nombre as cliente_nombre FROM casos c
           JOIN clientes cl ON c.cliente_id = cl.id
           WHERE c.abogado_id=? AND c.estado = 'activo'
           ORDER BY c.created_at DESC LIMIT 5""",
        (user_id,)
    ).fetchall()

    return render_template(
        'abogado/dashboard.html',
        casos_activos=casos_activos,
        ingresos_total=ingresos_total,
        audiencias_proximas=[dict(a) for a in audiencias_proximas],
        casos_criticos=[dict(c) for c in casos_criticos],
    )


@abogado_bp.route('/casos')
@role_required('abogado')
def casos():
    db = get_db()
    clientes = db.execute(
        "SELECT id, nombre FROM clientes WHERE abogado_asignado_id=? ORDER BY nombre",
        (session['user_id'],)
    ).fetchall()
    return render_template('abogado/casos.html', clientes=[dict(c) for c in clientes])


@abogado_bp.route('/agenda')
@role_required('abogado')
def agenda():
    db = get_db()
    casos_lista = db.execute(
        "SELECT id, expediente, titulo FROM casos WHERE abogado_id=? ORDER BY expediente",
        (session['user_id'],)
    ).fetchall()
    return render_template('abogado/agenda.html', casos_lista=[dict(c) for c in casos_lista])


@abogado_bp.route('/clientes')
@role_required('abogado')
def clientes():
    return render_template('abogado/clientes.html')


@abogado_bp.route('/documentos')
@role_required('abogado')
def documentos():
    db = get_db()
    casos_lista = db.execute(
        "SELECT id, expediente, titulo FROM casos WHERE abogado_id=? ORDER BY expediente",
        (session['user_id'],)
    ).fetchall()
    return render_template('abogado/documentos.html', casos_lista=[dict(c) for c in casos_lista])


@abogado_bp.route('/facturacion')
@role_required('abogado')
def facturacion():
    return render_template('abogado/facturacion.html')
