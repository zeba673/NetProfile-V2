"""
app/blueprints/secretaria/routes.py — Rutas del panel del Secretario/a
"""
from flask import render_template, session
from app.blueprints.secretaria import secretaria_bp
from app.blueprints.auth.routes import role_required
from app import get_db


@secretaria_bp.route('/dashboard')
@role_required('secretaria')
def dashboard():
    db = get_db()

    tareas = db.execute(
        "SELECT * FROM tareas ORDER BY completada ASC, prioridad DESC, fecha_limite ASC LIMIT 10"
    ).fetchall()

    recepciones_hoy = db.execute(
        """SELECT * FROM audiencias_agenda
           WHERE tipo='recepcion' AND DATE(fecha_hora)=DATE('now')
           ORDER BY fecha_hora"""
    ).fetchall()

    casos_activos = db.execute(
        "SELECT COUNT(*) as c FROM casos WHERE estado IN ('activo','en_curso')"
    ).fetchone()['c']

    tareas_pendientes = db.execute(
        "SELECT COUNT(*) as c FROM tareas WHERE completada=0"
    ).fetchone()['c']

    return render_template(
        'secretaria/dashboard.html',
        tareas=[dict(t) for t in tareas],
        recepciones_hoy=[dict(r) for r in recepciones_hoy],
        casos_activos=casos_activos,
        tareas_pendientes=tareas_pendientes,
    )


@secretaria_bp.route('/agenda')
@role_required('secretaria')
def agenda():
    db = get_db()
    casos_lista = db.execute(
        "SELECT id, expediente, titulo FROM casos ORDER BY expediente"
    ).fetchall()
    abogados = db.execute(
        "SELECT id, nombre_completo FROM usuarios WHERE rol='abogado'"
    ).fetchall()
    return render_template(
        'secretaria/agenda.html',
        casos_lista=[dict(c) for c in casos_lista],
        abogados=[dict(a) for a in abogados]
    )


@secretaria_bp.route('/casos')
@role_required('secretaria')
def casos():
    db = get_db()
    clientes = db.execute("SELECT id, nombre FROM clientes ORDER BY nombre").fetchall()
    abogados = db.execute("SELECT id, nombre_completo FROM usuarios WHERE rol='abogado'").fetchall()
    return render_template(
        'secretaria/casos.html',
        clientes=[dict(c) for c in clientes],
        abogados=[dict(a) for a in abogados]
    )


@secretaria_bp.route('/clientes')
@role_required('secretaria')
def clientes():
    db = get_db()
    abogados = db.execute("SELECT id, nombre_completo FROM usuarios WHERE rol='abogado'").fetchall()
    return render_template('secretaria/clientes.html', abogados=[dict(a) for a in abogados])


@secretaria_bp.route('/caja')
@role_required('secretaria')
def caja():
    db = get_db()
    saldo = db.execute(
        """SELECT COALESCE(SUM(CASE WHEN tipo='ingreso' THEN monto ELSE -monto END), 0) as s
           FROM movimientos_caja"""
    ).fetchone()['s']
    ingresos = db.execute(
        "SELECT COALESCE(SUM(monto),0) as t FROM movimientos_caja WHERE tipo='ingreso'"
    ).fetchone()['t']
    egresos = db.execute(
        "SELECT COALESCE(SUM(monto),0) as t FROM movimientos_caja WHERE tipo='egreso'"
    ).fetchone()['t']
    return render_template('secretaria/caja.html', saldo=saldo, ingresos=ingresos, egresos=egresos)
