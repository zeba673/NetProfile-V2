"""
init_db.py — Inicializa la base de datos y carga datos de prueba.
Ejecutar una sola vez: python init_db.py
"""
import sqlite3
import bcrypt
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'lexis.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')


def get_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')


def init():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    if os.path.exists(DB_PATH):
        print(f"[!] Base de datos ya existe en: {DB_PATH}")
        if '--force' not in sys.argv:
            print("    Usá --force para reinicializar.")
            return
        os.remove(DB_PATH)
        print("    Base de datos eliminada. Reinicializando...")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Aplicar schema
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())

    print("[+] Schema aplicado correctamente.")

    # Insertar usuarios de prueba
    usuarios = [
        ('jsmith',  get_hash('demo123'), 'abogado',    'Dr. Juan Smith'),
        ('mgarcia', get_hash('demo123'), 'secretaria', 'María García'),
        ('rlopez',  get_hash('demo123'), 'abogado',    'Dr. Roberto López'),
    ]
    conn.executemany(
        "INSERT INTO usuarios (usuario, password_hash, rol, nombre_completo) VALUES (?, ?, ?, ?)",
        usuarios
    )

    # Obtener IDs
    abogado1_id = conn.execute("SELECT id FROM usuarios WHERE usuario = 'jsmith'").fetchone()['id']
    abogado2_id = conn.execute("SELECT id FROM usuarios WHERE usuario = 'rlopez'").fetchone()['id']
    secretaria_id = conn.execute("SELECT id FROM usuarios WHERE usuario = 'mgarcia'").fetchone()['id']

    # Insertar clientes de prueba
    clientes = [
        ('20-12345678-3', 'Constructora Méndez S.A.',    '+54 11 4567-8901', 'contacto@mendez.com.ar',    'Av. Corrientes 1234, CABA', 'Cliente corporativo, facturación mensual', abogado1_id),
        ('27-98765432-1', 'Laura Fernández',              '+54 9 11 2345-6789', 'lfernandez@gmail.com',   'Belgrano 456, San Isidro',   'Caso civil pendiente',                    abogado1_id),
        ('30-87654321-5', 'Importadora Del Sur S.R.L.',  '+54 11 3456-7890', 'legal@delsur.com.ar',      'Madero 789, Puerto Madero',  'Litigio comercial activo',                abogado2_id),
        ('20-45678901-2', 'Carlos Ruiz',                  '+54 9 11 8765-4321', 'c.ruiz@hotmail.com',    'Libertad 321, Palermo',      'Consulta sucesoria',                      abogado1_id),
        ('27-34567890-4', 'Technovate Argentina S.A.',   '+54 11 5678-9012', 'legal@technovate.com.ar',  'Reconquista 555, Microcentro','Contrato laboral en revisión',            abogado2_id),
    ]
    conn.executemany(
        "INSERT INTO clientes (dni_cuit, nombre, telefono, email, direccion, notas, abogado_asignado_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        clientes
    )

    cliente_ids = [row['id'] for row in conn.execute("SELECT id FROM clientes ORDER BY id").fetchall()]

    # Insertar casos de prueba
    casos = [
        ('EXP-2024-001', 'Mendez vs. Municipalidad',           'Impugnación de obra pública',                  cliente_ids[0], abogado1_id, 'activo',   'Prioridad alta. Audiencia próxima semana. Revisar peritos.'),
        ('EXP-2024-002', 'Fernández - Divorcio Contencioso',   'Proceso de divorcio con disputa de bienes',    cliente_ids[1], abogado1_id, 'en_curso', 'Acordar con contraparte. Oferta de mediación en análisis.'),
        ('EXP-2024-003', 'Del Sur - Incumplimiento Comercial', 'Demanda por incumplimiento de contrato',       cliente_ids[2], abogado2_id, 'activo',   'Documentación de contrato enviada. Esperar respuesta.'),
        ('EXP-2024-004', 'Ruiz - Sucesión Intestada',          'Proceso sucesorio sin testamento',             cliente_ids[3], abogado1_id, 'en_curso', 'Inventario de bienes completo. Paso siguiente: declaratoria.'),
        ('EXP-2024-005', 'Technovate - Laboral',               'Conflicto laboral por despido sin causa',      cliente_ids[4], abogado2_id, 'activo',   'Negociación en curso. Evaluar acuerdo extrajudicial.'),
        ('EXP-2023-089', 'Méndez - Contrato de Locación',      'Renovación y disputa de contrato de alquiler', cliente_ids[0], abogado1_id, 'cerrado',  'Resuelto favorablemente. Archivado.'),
    ]
    conn.executemany(
        "INSERT INTO casos (expediente, titulo, descripcion, cliente_id, abogado_id, estado, nota_estrategica) VALUES (?, ?, ?, ?, ?, ?, ?)",
        casos
    )

    caso_ids = [row['id'] for row in conn.execute("SELECT id FROM casos ORDER BY id").fetchall()]

    # Insertar audiencias de prueba
    audiencias = [
        (caso_ids[0], 'Audiencia de Vista de Causa',       '2026-07-02 10:00', 'audiencia', 'confirmada', 'Sala 4, Juzgado Civil N°12'),
        (caso_ids[1], 'Mediación Prejudicial',              '2026-07-05 14:30', 'reunion',   'pendiente',  'Centro de Mediación CABA'),
        (caso_ids[2], 'Reunión con Perito Contable',        '2026-07-03 09:00', 'reunion',   'confirmada', 'Oficina del perito'),
        (caso_ids[3], 'Declaratoria de Herederos',          '2026-07-10 11:00', 'audiencia', 'pendiente',  'Juzgado Civil N°8'),
        (None,        'Recepción - Nuevo Cliente Potencial','2026-07-01 16:00', 'recepcion', 'confirmada', 'Oficina del estudio'),
        (caso_ids[4], 'Audiencia Laboral',                  '2026-07-08 10:30', 'audiencia', 'pendiente',  'Juzgado del Trabajo N°5'),
        (None,        'Reunión de Equipo Semanal',          '2026-06-30 09:00', 'reunion',   'confirmada', 'Sala de reuniones principal'),
    ]
    conn.executemany(
        "INSERT INTO audiencias_agenda (caso_id, titulo, fecha_hora, tipo, estado, descripcion) VALUES (?, ?, ?, ?, ?, ?)",
        audiencias
    )

    # Insertar documentos de prueba
    documentos = [
        (caso_ids[0], 'Escrito de Demanda.pdf',          'uploads/demanda_001.pdf',       'Demanda',          'digitalizado'),
        (caso_ids[0], 'Prueba Pericial - Planos.pdf',    None,                            'Pericia',          'pendiente_escaneo'),
        (caso_ids[1], 'Acta Matrimonial.pdf',            'uploads/acta_mat_002.pdf',      'Acta',             'digitalizado'),
        (caso_ids[2], 'Contrato Comercial 2023.pdf',     'uploads/contrato_003.pdf',      'Contrato',         'digitalizado'),
        (caso_ids[3], 'Certificado de Defunción.pdf',    None,                            'Certificado',      'pendiente_escaneo'),
        (caso_ids[4], 'Telegrama de Despido.pdf',        'uploads/telegrama_005.pdf',     'Notificación',     'digitalizado'),
        (caso_ids[4], 'Recibo de Sueldo - Dic 2025.pdf', None,                            'Comprobante',      'pendiente_escaneo'),
    ]
    conn.executemany(
        "INSERT INTO documentos (caso_id, nombre_archivo, ruta_archivo, tipo_doc, estado) VALUES (?, ?, ?, ?, ?)",
        documentos
    )

    # Insertar movimientos de caja de prueba
    movimientos = [
        ('ingreso', 85000.00,  'Honorarios - Exp. 2024-001 (Méndez)',       'honorarios',   '2026-06-20', 'completado',  abogado1_id),
        ('ingreso', 42000.00,  'Anticipo de Honorarios - Exp. 2024-002',    'honorarios',   '2026-06-18', 'completado',  abogado1_id),
        ('egreso',  12500.00,  'Sellado judicial - Exp. 2024-003',          'gastos_judic', '2026-06-19', 'completado',  secretaria_id),
        ('ingreso', 120000.00, 'Honorarios - Exp. 2024-003 (Del Sur)',      'honorarios',   '2026-06-22', 'completado',  abogado2_id),
        ('egreso',  8900.00,   'Honorarios perito contable',                'peritos',      '2026-06-21', 'completado',  secretaria_id),
        ('egreso',  3200.00,   'Fotocopias y certificaciones',              'admin',        '2026-06-23', 'completado',  secretaria_id),
        ('ingreso', 65000.00,  'Honorarios - Exp. 2024-005 (Technovate)',   'honorarios',   '2026-06-24', 'procesando',  abogado2_id),
        ('egreso',  15000.00,  'Alquiler oficina - Junio 2026',             'alquiler',     '2026-06-01', 'completado',  secretaria_id),
        ('egreso',  4500.00,   'Servicios (Internet + Tel)',                'servicios',    '2026-06-05', 'completado',  secretaria_id),
        ('ingreso', 30000.00,  'Consulta - Nuevo cliente potencial',        'consultas',    '2026-06-24', 'completado',  abogado1_id),
    ]
    conn.executemany(
        "INSERT INTO movimientos_caja (tipo, monto, descripcion, categoria, fecha, estado, usuario_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        movimientos
    )

    # Insertar tareas de prueba
    tareas = [
        ('Preparar escrito de contestación - Exp. 2024-003', 0, '2026-07-02', 'alta',    secretaria_id),
        ('Notificar a cliente Fernández sobre mediación',    0, '2026-06-28', 'urgente', secretaria_id),
        ('Revisar documentación de Technovate',              0, '2026-07-01', 'normal',  secretaria_id),
        ('Coordinar peritos para Exp. 2024-001',             1, '2026-06-25', 'alta',    secretaria_id),
        ('Actualizar legajos digitales',                     0, '2026-07-05', 'baja',    secretaria_id),
        ('Enviar factura a Importadora Del Sur',             0, '2026-06-27', 'normal',  secretaria_id),
        ('Archivar expediente 2023-089',                     1, '2026-06-20', 'baja',    secretaria_id),
    ]
    conn.executemany(
        "INSERT INTO tareas (descripcion, completada, fecha_limite, prioridad, asignada_a) VALUES (?, ?, ?, ?, ?)",
        tareas
    )

    conn.commit()
    conn.close()

    print("[+] Datos de prueba insertados.")
    print("[+] ========================================")
    print("[+] Base de datos inicializada exitosamente.")
    print("[+] ========================================")
    print()
    print("    Usuarios de acceso:")
    print("    ┌─────────────┬────────────┬─────────────┐")
    print("    │ Usuario     │ Contraseña │ Rol         │")
    print("    ├─────────────┼────────────┼─────────────┤")
    print("    │ jsmith      │ demo123    │ Abogado     │")
    print("    │ mgarcia     │ demo123    │ Secretaria  │")
    print("    │ rlopez      │ demo123    │ Abogado     │")
    print("    └─────────────┴────────────┴─────────────┘")


if __name__ == '__main__':
    init()
