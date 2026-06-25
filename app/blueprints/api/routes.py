"""
app/blueprints/api/routes.py — API JSON completa (CRUD universal)
Todos los endpoints retornan JSON y son consumidos vía fetch() desde el frontend.
"""
from flask import request, jsonify, session
from app.blueprints.api import api_bp
from app import get_db
from app.blueprints.auth.routes import login_required


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────
def row_to_dict(row):
    return dict(row) if row else None


def rows_to_list(rows):
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────
#  DASHBOARD / KPIs
# ─────────────────────────────────────────────
@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    db = get_db()
    rol = session.get('rol')
    user_id = session.get('user_id')

    if rol == 'abogado':
        casos_activos = db.execute(
            "SELECT COUNT(*) as c FROM casos WHERE abogado_id = ? AND estado IN ('activo', 'en_curso')",
            (user_id,)
        ).fetchone()['c']

        ingresos = db.execute(
            "SELECT COALESCE(SUM(monto), 0) as total FROM movimientos_caja WHERE tipo = 'ingreso' AND usuario_id = ?",
            (user_id,)
        ).fetchone()['total']

        audiencias_pendientes = db.execute(
            """SELECT COUNT(*) as c FROM audiencias_agenda aa
               JOIN casos c ON aa.caso_id = c.id
               WHERE c.abogado_id = ? AND aa.estado = 'pendiente'""",
            (user_id,)
        ).fetchone()['c']

        clientes = db.execute(
            "SELECT COUNT(*) as c FROM clientes WHERE abogado_asignado_id = ?",
            (user_id,)
        ).fetchone()['c']

    else:
        casos_activos = db.execute(
            "SELECT COUNT(*) as c FROM casos WHERE estado IN ('activo', 'en_curso')"
        ).fetchone()['c']

        ingresos = db.execute(
            "SELECT COALESCE(SUM(monto), 0) as total FROM movimientos_caja WHERE tipo = 'ingreso'"
        ).fetchone()['total']

        audiencias_pendientes = db.execute(
            "SELECT COUNT(*) as c FROM audiencias_agenda WHERE estado = 'pendiente'"
        ).fetchone()['c']

        clientes = db.execute("SELECT COUNT(*) as c FROM clientes").fetchone()['c']

    saldo = db.execute(
        """SELECT COALESCE(SUM(CASE WHEN tipo='ingreso' THEN monto ELSE -monto END), 0) as s
           FROM movimientos_caja"""
    ).fetchone()['s']

    tareas_pendientes = db.execute(
        "SELECT COUNT(*) as c FROM tareas WHERE completada = 0"
    ).fetchone()['c']

    return jsonify({
        'casos_activos': casos_activos,
        'ingresos_total': ingresos,
        'audiencias_pendientes': audiencias_pendientes,
        'clientes': clientes,
        'saldo_caja': saldo,
        'tareas_pendientes': tareas_pendientes,
    })


# ─────────────────────────────────────────────
#  CASOS
# ─────────────────────────────────────────────
@api_bp.route('/casos', methods=['GET'])
@login_required
def get_casos():
    db = get_db()
    rol = session.get('rol')
    user_id = session.get('user_id')

    if rol == 'abogado':
        rows = db.execute(
            """SELECT c.*, cl.nombre as cliente_nombre, u.nombre_completo as abogado_nombre
               FROM casos c
               JOIN clientes cl ON c.cliente_id = cl.id
               JOIN usuarios u ON c.abogado_id = u.id
               WHERE c.abogado_id = ?
               ORDER BY c.created_at DESC""",
            (user_id,)
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT c.*, cl.nombre as cliente_nombre, u.nombre_completo as abogado_nombre
               FROM casos c
               JOIN clientes cl ON c.cliente_id = cl.id
               JOIN usuarios u ON c.abogado_id = u.id
               ORDER BY c.created_at DESC"""
        ).fetchall()

    return jsonify(rows_to_list(rows))


@api_bp.route('/casos', methods=['POST'])
@login_required
def create_caso():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400

    required = ['expediente', 'titulo', 'cliente_id', 'abogado_id']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Campo requerido: {field}'}), 400

    db = get_db()
    try:
        cursor = db.execute(
            """INSERT INTO casos (expediente, titulo, descripcion, cliente_id, abogado_id, estado, nota_estrategica)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (data['expediente'], data['titulo'], data.get('descripcion', ''),
             data['cliente_id'], data['abogado_id'], data.get('estado', 'activo'),
             data.get('nota_estrategica', ''))
        )
        db.commit()
        caso = db.execute(
            """SELECT c.*, cl.nombre as cliente_nombre, u.nombre_completo as abogado_nombre
               FROM casos c JOIN clientes cl ON c.cliente_id = cl.id
               JOIN usuarios u ON c.abogado_id = u.id WHERE c.id = ?""",
            (cursor.lastrowid,)
        ).fetchone()
        return jsonify({'success': True, 'caso': row_to_dict(caso)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/casos/<int:caso_id>', methods=['PUT'])
@login_required
def update_caso(caso_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400

    db = get_db()
    caso = db.execute("SELECT * FROM casos WHERE id = ?", (caso_id,)).fetchone()
    if not caso:
        return jsonify({'error': 'Caso no encontrado'}), 404

    db.execute(
        """UPDATE casos SET titulo=?, descripcion=?, estado=?, nota_estrategica=?,
           updated_at=datetime('now') WHERE id=?""",
        (data.get('titulo', caso['titulo']),
         data.get('descripcion', caso['descripcion']),
         data.get('estado', caso['estado']),
         data.get('nota_estrategica', caso['nota_estrategica']),
         caso_id)
    )
    db.commit()
    updated = db.execute(
        """SELECT c.*, cl.nombre as cliente_nombre, u.nombre_completo as abogado_nombre
           FROM casos c JOIN clientes cl ON c.cliente_id = cl.id
           JOIN usuarios u ON c.abogado_id = u.id WHERE c.id = ?""",
        (caso_id,)
    ).fetchone()
    return jsonify({'success': True, 'caso': row_to_dict(updated)})


@api_bp.route('/casos/<int:caso_id>', methods=['DELETE'])
@login_required
def delete_caso(caso_id):
    db = get_db()
    caso = db.execute("SELECT * FROM casos WHERE id = ?", (caso_id,)).fetchone()
    if not caso:
        return jsonify({'error': 'Caso no encontrado'}), 404
    db.execute("DELETE FROM casos WHERE id = ?", (caso_id,))
    db.commit()
    return jsonify({'success': True})


# ─────────────────────────────────────────────
#  CLIENTES
# ─────────────────────────────────────────────
@api_bp.route('/clientes', methods=['GET'])
@login_required
def get_clientes():
    db = get_db()
    rol = session.get('rol')
    user_id = session.get('user_id')

    if rol == 'abogado':
        rows = db.execute(
            """SELECT c.*, u.nombre_completo as abogado_nombre
               FROM clientes c LEFT JOIN usuarios u ON c.abogado_asignado_id = u.id
               WHERE c.abogado_asignado_id = ? ORDER BY c.nombre""",
            (user_id,)
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT c.*, u.nombre_completo as abogado_nombre
               FROM clientes c LEFT JOIN usuarios u ON c.abogado_asignado_id = u.id
               ORDER BY c.nombre"""
        ).fetchall()

    return jsonify(rows_to_list(rows))


@api_bp.route('/clientes', methods=['POST'])
@login_required
def create_cliente():
    data = request.get_json()
    if not data or not data.get('nombre') or not data.get('dni_cuit'):
        return jsonify({'error': 'Nombre y DNI/CUIT son requeridos'}), 400

    db = get_db()
    try:
        cursor = db.execute(
            """INSERT INTO clientes (dni_cuit, nombre, telefono, email, direccion, notas, abogado_asignado_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (data['dni_cuit'], data['nombre'], data.get('telefono', ''),
             data.get('email', ''), data.get('direccion', ''),
             data.get('notas', ''), data.get('abogado_asignado_id'))
        )
        db.commit()
        cliente = db.execute(
            """SELECT c.*, u.nombre_completo as abogado_nombre
               FROM clientes c LEFT JOIN usuarios u ON c.abogado_asignado_id = u.id
               WHERE c.id = ?""",
            (cursor.lastrowid,)
        ).fetchone()
        return jsonify({'success': True, 'cliente': row_to_dict(cliente)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/clientes/<int:cliente_id>', methods=['PUT'])
@login_required
def update_cliente(cliente_id):
    data = request.get_json()
    db = get_db()
    cliente = db.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404

    db.execute(
        """UPDATE clientes SET dni_cuit=?, nombre=?, telefono=?, email=?,
           direccion=?, notas=?, abogado_asignado_id=? WHERE id=?""",
        (data.get('dni_cuit', cliente['dni_cuit']),
         data.get('nombre', cliente['nombre']),
         data.get('telefono', cliente['telefono']),
         data.get('email', cliente['email']),
         data.get('direccion', cliente['direccion']),
         data.get('notas', cliente['notas']),
         data.get('abogado_asignado_id', cliente['abogado_asignado_id']),
         cliente_id)
    )
    db.commit()
    return jsonify({'success': True})


@api_bp.route('/clientes/<int:cliente_id>', methods=['DELETE'])
@login_required
def delete_cliente(cliente_id):
    db = get_db()
    db.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    db.commit()
    return jsonify({'success': True})


# ─────────────────────────────────────────────
#  AUDIENCIAS
# ─────────────────────────────────────────────
@api_bp.route('/audiencias', methods=['GET'])
@login_required
def get_audiencias():
    db = get_db()
    rol = session.get('rol')
    user_id = session.get('user_id')

    if rol == 'abogado':
        rows = db.execute(
            """SELECT aa.*, c.expediente, c.titulo as caso_titulo, c.abogado_id
               FROM audiencias_agenda aa
               LEFT JOIN casos c ON aa.caso_id = c.id
               WHERE c.abogado_id = ? OR aa.caso_id IS NULL
               ORDER BY aa.fecha_hora""",
            (user_id,)
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT aa.*, c.expediente, c.titulo as caso_titulo
               FROM audiencias_agenda aa
               LEFT JOIN casos c ON aa.caso_id = c.id
               ORDER BY aa.fecha_hora"""
        ).fetchall()

    return jsonify(rows_to_list(rows))


@api_bp.route('/audiencias', methods=['POST'])
@login_required
def create_audiencia():
    data = request.get_json()
    if not data or not data.get('titulo') or not data.get('fecha_hora'):
        return jsonify({'error': 'Título y fecha/hora son requeridos'}), 400

    db = get_db()
    cursor = db.execute(
        """INSERT INTO audiencias_agenda (caso_id, titulo, fecha_hora, tipo, estado, descripcion)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (data.get('caso_id'), data['titulo'], data['fecha_hora'],
         data.get('tipo', 'audiencia'), data.get('estado', 'pendiente'),
         data.get('descripcion', ''))
    )
    db.commit()
    audiencia = db.execute(
        """SELECT aa.*, c.expediente, c.titulo as caso_titulo
           FROM audiencias_agenda aa LEFT JOIN casos c ON aa.caso_id = c.id
           WHERE aa.id = ?""",
        (cursor.lastrowid,)
    ).fetchone()
    return jsonify({'success': True, 'audiencia': row_to_dict(audiencia)}), 201


@api_bp.route('/audiencias/<int:aud_id>', methods=['PUT'])
@login_required
def update_audiencia(aud_id):
    data = request.get_json()
    db = get_db()
    aud = db.execute("SELECT * FROM audiencias_agenda WHERE id = ?", (aud_id,)).fetchone()
    if not aud:
        return jsonify({'error': 'Audiencia no encontrada'}), 404

    db.execute(
        """UPDATE audiencias_agenda SET titulo=?, fecha_hora=?, tipo=?, estado=?, descripcion=?
           WHERE id=?""",
        (data.get('titulo', aud['titulo']),
         data.get('fecha_hora', aud['fecha_hora']),
         data.get('tipo', aud['tipo']),
         data.get('estado', aud['estado']),
         data.get('descripcion', aud['descripcion']),
         aud_id)
    )
    db.commit()
    return jsonify({'success': True})


@api_bp.route('/audiencias/<int:aud_id>', methods=['DELETE'])
@login_required
def delete_audiencia(aud_id):
    db = get_db()
    db.execute("DELETE FROM audiencias_agenda WHERE id = ?", (aud_id,))
    db.commit()
    return jsonify({'success': True})


# ─────────────────────────────────────────────
#  MOVIMIENTOS DE CAJA
# ─────────────────────────────────────────────
@api_bp.route('/movimientos', methods=['GET'])
@login_required
def get_movimientos():
    db = get_db()
    rows = db.execute(
        """SELECT m.*, u.nombre_completo as usuario_nombre
           FROM movimientos_caja m LEFT JOIN usuarios u ON m.usuario_id = u.id
           ORDER BY m.created_at DESC"""
    ).fetchall()
    return jsonify(rows_to_list(rows))


@api_bp.route('/movimientos', methods=['POST'])
@login_required
def create_movimiento():
    data = request.get_json()
    if not data or not data.get('tipo') or not data.get('monto') or not data.get('descripcion'):
        return jsonify({'error': 'Tipo, monto y descripción son requeridos'}), 400

    db = get_db()
    user_id = session.get('user_id')
    cursor = db.execute(
        """INSERT INTO movimientos_caja (tipo, monto, descripcion, categoria, fecha, estado, usuario_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (data['tipo'], float(data['monto']), data['descripcion'],
         data.get('categoria', 'general'), data.get('fecha', 'date("now")'),
         data.get('estado', 'completado'), user_id)
    )
    db.commit()

    mov = db.execute(
        """SELECT m.*, u.nombre_completo as usuario_nombre
           FROM movimientos_caja m LEFT JOIN usuarios u ON m.usuario_id = u.id
           WHERE m.id = ?""",
        (cursor.lastrowid,)
    ).fetchone()

    saldo = db.execute(
        """SELECT COALESCE(SUM(CASE WHEN tipo='ingreso' THEN monto ELSE -monto END), 0) as s
           FROM movimientos_caja"""
    ).fetchone()['s']

    return jsonify({'success': True, 'movimiento': row_to_dict(mov), 'nuevo_saldo': saldo}), 201


@api_bp.route('/movimientos/<int:mov_id>', methods=['DELETE'])
@login_required
def delete_movimiento(mov_id):
    db = get_db()
    db.execute("DELETE FROM movimientos_caja WHERE id = ?", (mov_id,))
    db.commit()
    return jsonify({'success': True})


# ─────────────────────────────────────────────
#  TAREAS
# ─────────────────────────────────────────────
@api_bp.route('/tareas', methods=['GET'])
@login_required
def get_tareas():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM tareas ORDER BY completada ASC, prioridad DESC, fecha_limite ASC"
    ).fetchall()
    return jsonify(rows_to_list(rows))


@api_bp.route('/tareas', methods=['POST'])
@login_required
def create_tarea():
    data = request.get_json()
    if not data or not data.get('descripcion'):
        return jsonify({'error': 'Descripción requerida'}), 400

    db = get_db()
    user_id = session.get('user_id')
    cursor = db.execute(
        "INSERT INTO tareas (descripcion, completada, fecha_limite, prioridad, asignada_a) VALUES (?, 0, ?, ?, ?)",
        (data['descripcion'], data.get('fecha_limite'), data.get('prioridad', 'normal'), user_id)
    )
    db.commit()
    tarea = db.execute("SELECT * FROM tareas WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify({'success': True, 'tarea': row_to_dict(tarea)}), 201


@api_bp.route('/tareas/<int:tarea_id>', methods=['PUT'])
@login_required
def update_tarea(tarea_id):
    data = request.get_json()
    db = get_db()
    tarea = db.execute("SELECT * FROM tareas WHERE id = ?", (tarea_id,)).fetchone()
    if not tarea:
        return jsonify({'error': 'Tarea no encontrada'}), 404

    db.execute(
        "UPDATE tareas SET descripcion=?, completada=?, fecha_limite=?, prioridad=? WHERE id=?",
        (data.get('descripcion', tarea['descripcion']),
         int(data.get('completada', tarea['completada'])),
         data.get('fecha_limite', tarea['fecha_limite']),
         data.get('prioridad', tarea['prioridad']),
         tarea_id)
    )
    db.commit()
    return jsonify({'success': True})


@api_bp.route('/tareas/<int:tarea_id>', methods=['DELETE'])
@login_required
def delete_tarea(tarea_id):
    db = get_db()
    db.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
    db.commit()
    return jsonify({'success': True})


# ─────────────────────────────────────────────
#  DOCUMENTOS
# ─────────────────────────────────────────────
@api_bp.route('/documentos', methods=['GET'])
@login_required
def get_documentos():
    db = get_db()
    rol = session.get('rol')
    user_id = session.get('user_id')

    if rol == 'abogado':
        rows = db.execute(
            """SELECT d.*, c.expediente, c.titulo as caso_titulo
               FROM documentos d LEFT JOIN casos c ON d.caso_id = c.id
               WHERE c.abogado_id = ?
               ORDER BY d.created_at DESC""",
            (user_id,)
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT d.*, c.expediente, c.titulo as caso_titulo
               FROM documentos d LEFT JOIN casos c ON d.caso_id = c.id
               ORDER BY d.created_at DESC"""
        ).fetchall()

    return jsonify(rows_to_list(rows))


@api_bp.route('/documentos', methods=['POST'])
@login_required
def create_documento():
    import os
    import uuid
    from werkzeug.utils import secure_filename
    from flask import current_app

    # Check if request has files (multipart/form-data) and the file is not empty
    if 'archivo' in request.files and request.files['archivo'].filename != '':
        file = request.files['archivo']
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate a unique filename using UUID to avoid overwriting existing files
        base, ext = os.path.splitext(filename)
        unique_filename = f"{base}_{uuid.uuid4().hex[:8]}{ext.lower()}"
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # Path relative to static directory
        ruta_archivo = f'uploads/{unique_filename}'
        
        # Form values
        caso_id = request.form.get('caso_id')
        nombre_archivo = request.form.get('nombre_archivo') or filename
        tipo_doc = request.form.get('tipo_doc', '')
        estado = request.form.get('estado', 'digitalizado')
        notas = request.form.get('notas', '')
    else:
        # Fallback to Form fields or JSON request
        if request.form:
            nombre_archivo = request.form.get('nombre_archivo')
            caso_id = request.form.get('caso_id')
            tipo_doc = request.form.get('tipo_doc', '')
            estado = request.form.get('estado', 'pendiente_escaneo')
            notas = request.form.get('notas', '')
            ruta_archivo = None
        else:
            data = request.get_json() or {}
            nombre_archivo = data.get('nombre_archivo')
            caso_id = data.get('caso_id')
            tipo_doc = data.get('tipo_doc', '')
            estado = data.get('estado', 'pendiente_escaneo')
            notas = data.get('notas', '')
            ruta_archivo = data.get('ruta_archivo')

        if not nombre_archivo:
            return jsonify({'error': 'Nombre de archivo requerido'}), 400

    # Common parsing for caso_id
    if caso_id == '' or caso_id == 'null' or caso_id is None:
        caso_id = None
    else:
        try:
            caso_id = int(caso_id)
        except ValueError:
            caso_id = None

    db = get_db()
    cursor = db.execute(
        "INSERT INTO documentos (caso_id, nombre_archivo, ruta_archivo, tipo_doc, estado, notas) VALUES (?, ?, ?, ?, ?, ?)",
        (caso_id, nombre_archivo, ruta_archivo, tipo_doc, estado, notas)
    )
    db.commit()
    doc = db.execute(
        """SELECT d.*, c.expediente, c.titulo as caso_titulo
           FROM documentos d LEFT JOIN casos c ON d.caso_id = c.id
           WHERE d.id = ?""",
        (cursor.lastrowid,)
    ).fetchone()
    return jsonify({'success': True, 'documento': row_to_dict(doc)}), 201


@api_bp.route('/documentos/<int:doc_id>', methods=['PUT'])
@login_required
def update_documento(doc_id):
    data = request.get_json()
    db = get_db()
    doc = db.execute("SELECT * FROM documentos WHERE id = ?", (doc_id,)).fetchone()
    if not doc:
        return jsonify({'error': 'Documento no encontrado'}), 404

    db.execute(
        "UPDATE documentos SET estado=?, notas=? WHERE id=?",
        (data.get('estado', doc['estado']), data.get('notas', doc['notas']), doc_id)
    )
    db.commit()
    return jsonify({'success': True})


@api_bp.route('/documentos/<int:doc_id>', methods=['DELETE'])
@login_required
def delete_documento(doc_id):
    db = get_db()
    db.execute("DELETE FROM documentos WHERE id = ?", (doc_id,))
    db.commit()
    return jsonify({'success': True})


# ─────────────────────────────────────────────
#  USUARIOS (listado para selects)
# ─────────────────────────────────────────────
@api_bp.route('/usuarios/abogados', methods=['GET'])
@login_required
def get_abogados():
    db = get_db()
    rows = db.execute(
        "SELECT id, nombre_completo, usuario FROM usuarios WHERE rol = 'abogado' ORDER BY nombre_completo"
    ).fetchall()
    return jsonify(rows_to_list(rows))


@api_bp.route('/casos/lista', methods=['GET'])
@login_required
def get_casos_lista():
    db = get_db()
    rows = db.execute(
        "SELECT id, expediente, titulo FROM casos ORDER BY expediente"
    ).fetchall()
    return jsonify(rows_to_list(rows))
