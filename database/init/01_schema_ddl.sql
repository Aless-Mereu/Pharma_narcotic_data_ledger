-- Creación del Esquema Relacional GxP para Control de Estupefacientes

-- 1. Usuarios y Roles (RBAC)
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    mfa_secret VARCHAR(100) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    num_colegiado VARCHAR(50),
    rol VARCHAR(30) CHECK (rol IN ('OPERADOR', 'FARMACEUTICO', 'DIRECTOR_TECNICO', 'ADMIN')) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. Catálogo de Productos y Sustancias Estupefacientes
CREATE TABLE IF NOT EXISTS productos_estupefacientes (
    id_producto SERIAL PRIMARY KEY,
    codigo_nacional VARCHAR(20) UNIQUE NOT NULL,
    nombre_comercial VARCHAR(100) NOT NULL,
    principio_activo VARCHAR(100) NOT NULL,
    presentacion VARCHAR(100) NOT NULL,
    lista_estupefaciente VARCHAR(10) NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- 3. Libro Diario de Estupefacientes (GAMP 5 Append-Only)
CREATE TABLE IF NOT EXISTS libro_estupefacientes (
    id_movimiento BIGSERIAL PRIMARY KEY,
    id_producto INT REFERENCES productos_estupefacientes(id_producto) NOT NULL,
    tipo_movimiento VARCHAR(20) CHECK (tipo_movimiento IN ('ENTRADA', 'SALIDA', 'AJUSTE_MERMA', 'STORNO')) NOT NULL,
    num_lote VARCHAR(50) NOT NULL,
    fecha_caducidad DATE NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad <> 0),
    saldo_resultante INT NOT NULL CHECK (saldo_resultante >= 0),
    doc_referencia VARCHAR(100) NOT NULL,
    prescriptor_destino VARCHAR(150),
    motivo_ajuste TEXT,
    id_usuario_firma INT REFERENCES usuarios(id_usuario) NOT NULL,
    id_usuario_aprobacion INT REFERENCES usuarios(id_usuario),
    estado VARCHAR(20) DEFAULT 'CONFIRMADO' CHECK (estado IN ('PENDIENTE_APROBACION', 'CONFIRMADO', 'ANULADO')) NOT NULL,
    timestamp_servidor TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. Audit Trail Inmutable (Anexo 11 / 21 CFR Part 11)
CREATE TABLE IF NOT EXISTS audit_trail (
    id_audit BIGSERIAL PRIMARY KEY,
    tabla_afectada VARCHAR(50) NOT NULL,
    operacion VARCHAR(20) NOT NULL,
    id_registro_afectado BIGINT,
    id_usuario INT,
    ip_origen VARCHAR(45),
    timestamp_ntp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    datos_anteriores JSONB,
    datos_nuevos JSONB
);