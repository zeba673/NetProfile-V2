-- ============================================================
--  LEXIS STUDIO — Schema de Base de Datos PostgreSQL (Supabase)
--  Versión: 1.0 | Fecha: 2026
-- ============================================================

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id                SERIAL PRIMARY KEY,
    usuario           VARCHAR(100) NOT NULL UNIQUE,
    password_hash     VARCHAR(255) NOT NULL,
    rol               VARCHAR(20) NOT NULL CHECK(rol IN ('abogado', 'secretaria')),
    nombre_completo   VARCHAR(255) NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id                    SERIAL PRIMARY KEY,
    dni_cuit              VARCHAR(50) NOT NULL,
    nombre                VARCHAR(255) NOT NULL,
    telefono              VARCHAR(50),
    email                 VARCHAR(100),
    direccion             TEXT,
    notas                 TEXT,
    abogado_asignado_id   INTEGER,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (abogado_asignado_id) REFERENCES usuarios(id)
);

-- Tabla de Casos
CREATE TABLE IF NOT EXISTS casos (
    id                SERIAL PRIMARY KEY,
    expediente        VARCHAR(100) NOT NULL UNIQUE,
    titulo            VARCHAR(255) NOT NULL,
    descripcion       TEXT,
    cliente_id        INTEGER NOT NULL,
    abogado_id        INTEGER NOT NULL,
    estado            VARCHAR(50) NOT NULL DEFAULT 'activo' CHECK(estado IN ('activo', 'en_curso', 'cerrado', 'archivado')),
    nota_estrategica  TEXT,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (abogado_id) REFERENCES usuarios(id)
);

-- Tabla de Audiencias / Agenda
CREATE TABLE IF NOT EXISTS audiencias_agenda (
    id          SERIAL PRIMARY KEY,
    caso_id     INTEGER,
    titulo      VARCHAR(255) NOT NULL,
    fecha_hora  VARCHAR(100) NOT NULL,
    tipo        VARCHAR(50) NOT NULL DEFAULT 'audiencia' CHECK(tipo IN ('audiencia', 'reunion', 'recepcion')),
    estado      VARCHAR(50) NOT NULL DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'confirmada', 'cancelada', 'realizada')),
    descripcion TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (caso_id) REFERENCES casos(id)
);

-- Tabla de Documentos
CREATE TABLE IF NOT EXISTS documentos (
    id              SERIAL PRIMARY KEY,
    caso_id         INTEGER,
    nombre_archivo  VARCHAR(255) NOT NULL,
    ruta_archivo    TEXT,
    tipo_doc        VARCHAR(100),
    estado          VARCHAR(50) NOT NULL DEFAULT 'pendiente_escaneo' CHECK(estado IN ('pendiente_escaneo', 'digitalizado')),
    notas           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (caso_id) REFERENCES casos(id)
);

-- Tabla de Movimientos de Caja
CREATE TABLE IF NOT EXISTS movimientos_caja (
    id          SERIAL PRIMARY KEY,
    tipo        VARCHAR(20) NOT NULL CHECK(tipo IN ('ingreso', 'egreso')),
    monto       REAL NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    categoria   VARCHAR(100) DEFAULT 'general',
    fecha       VARCHAR(50) NOT NULL DEFAULT CURRENT_DATE::text,
    estado      VARCHAR(50) NOT NULL DEFAULT 'completado' CHECK(estado IN ('completado', 'procesando', 'fallido')),
    usuario_id  INTEGER,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de Tareas
CREATE TABLE IF NOT EXISTS tareas (
    id            SERIAL PRIMARY KEY,
    descripcion   TEXT NOT NULL,
    completada    INTEGER NOT NULL DEFAULT 0,
    fecha_limite  VARCHAR(50),
    prioridad     VARCHAR(50) DEFAULT 'normal' CHECK(prioridad IN ('baja', 'normal', 'alta', 'urgente')),
    asignada_a    INTEGER,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asignada_a) REFERENCES usuarios(id)
);
