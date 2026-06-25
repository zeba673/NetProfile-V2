-- ============================================================
--  LEXIS STUDIO — Schema de Base de Datos SQLite
--  Versión: 1.0 | Fecha: 2026
-- ============================================================

PRAGMA foreign_keys = ON;

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario           TEXT NOT NULL UNIQUE,
    password_hash     TEXT NOT NULL,
    rol               TEXT NOT NULL CHECK(rol IN ('abogado', 'secretaria')),
    nombre_completo   TEXT NOT NULL,
    created_at        TEXT DEFAULT (datetime('now'))
);

-- Tabla de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    dni_cuit              TEXT NOT NULL,
    nombre                TEXT NOT NULL,
    telefono              TEXT,
    email                 TEXT,
    direccion             TEXT,
    notas                 TEXT,
    abogado_asignado_id   INTEGER,
    created_at            TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (abogado_asignado_id) REFERENCES usuarios(id)
);

-- Tabla de Casos
CREATE TABLE IF NOT EXISTS casos (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    expediente        TEXT NOT NULL UNIQUE,
    titulo            TEXT NOT NULL,
    descripcion       TEXT,
    cliente_id        INTEGER NOT NULL,
    abogado_id        INTEGER NOT NULL,
    estado            TEXT NOT NULL DEFAULT 'activo' CHECK(estado IN ('activo', 'en_curso', 'cerrado', 'archivado')),
    nota_estrategica  TEXT,
    created_at        TEXT DEFAULT (datetime('now')),
    updated_at        TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (abogado_id) REFERENCES usuarios(id)
);

-- Tabla de Audiencias / Agenda
CREATE TABLE IF NOT EXISTS audiencias_agenda (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    caso_id     INTEGER,
    titulo      TEXT NOT NULL,
    fecha_hora  TEXT NOT NULL,
    tipo        TEXT NOT NULL DEFAULT 'audiencia' CHECK(tipo IN ('audiencia', 'reunion', 'recepcion')),
    estado      TEXT NOT NULL DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'confirmada', 'cancelada', 'realizada')),
    descripcion TEXT,
    created_at  TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (caso_id) REFERENCES casos(id)
);

-- Tabla de Documentos
CREATE TABLE IF NOT EXISTS documentos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    caso_id         INTEGER,
    nombre_archivo  TEXT NOT NULL,
    ruta_archivo    TEXT,
    tipo_doc        TEXT,
    estado          TEXT NOT NULL DEFAULT 'pendiente_escaneo' CHECK(estado IN ('pendiente_escaneo', 'digitalizado')),
    notas           TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (caso_id) REFERENCES casos(id)
);

-- Tabla de Movimientos de Caja
CREATE TABLE IF NOT EXISTS movimientos_caja (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo        TEXT NOT NULL CHECK(tipo IN ('ingreso', 'egreso')),
    monto       REAL NOT NULL,
    descripcion TEXT NOT NULL,
    categoria   TEXT DEFAULT 'general',
    fecha       TEXT NOT NULL DEFAULT (date('now')),
    estado      TEXT NOT NULL DEFAULT 'completado' CHECK(estado IN ('completado', 'procesando', 'fallido')),
    usuario_id  INTEGER,
    created_at  TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de Tareas
CREATE TABLE IF NOT EXISTS tareas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion   TEXT NOT NULL,
    completada    INTEGER NOT NULL DEFAULT 0,
    fecha_limite  TEXT,
    prioridad     TEXT DEFAULT 'normal' CHECK(prioridad IN ('baja', 'normal', 'alta', 'urgente')),
    asignada_a    INTEGER,
    created_at    TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (asignada_a) REFERENCES usuarios(id)
);
