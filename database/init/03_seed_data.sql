-- database/init/03_seed_data.sql
-- Datos iniciales de prueba (Seeds) para entorno de desarrollo y validación GxP

-- 1. Inserción de Usuarios de Prueba (Roles RBAC y secretos MFA)
-- Contraseña plana de prueba para todos: "GxPPass2026!" (almacenada con hash bcrypt)
INSERT INTO usuarios (username, password_hash, mfa_secret, nombre_completo, num_colegiado, rol, activo)
VALUES
    ('farmaceutico_regente', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'JBSWY3DPEHPK3PXP', 'Dra. Laura Martínez Gómez', 'COL-28-4451', 'FARMACEUTICO', true),
    ('director_calidad', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'JBSWY3DPEHPK3PXP', 'Dr. Carlos Ruiz Sanz', 'COL-28-1123', 'DIRECTOR_TECNICO', true),
    ('operador_planta', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'JBSWY3DPEHPK3PXP', 'Marc Soler Vidal', NULL, 'OPERADOR', true),
    ('admin_sistemas', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'JBSWY3DPEHPK3PXP', 'Admin IT Infrastructure', NULL, 'ADMIN', true)
ON CONFLICT (username) DO NOTHING;

-- 2. Catálogo Oficial de Medicamentos y Sustancias Estupefacientes (AEMPS / Convención 1961)
INSERT INTO productos_estupefacientes (codigo_nacional, nombre_comercial, principio_activo, presentacion, lista_estupefaciente, activo)
VALUES
    ('654321', 'Morfina Braun 10 mg/ml', 'Morfina hidrocloruro', 'Envase con 10 ampollas de 1 ml', 'Lista I', true),
    ('789123', 'Fentanilo Matrix 50 mcg/h', 'Fentanilo', 'Envase con 5 parches transdérmicos', 'Lista I', true),
    ('456789', 'Metasedin 5 mg', 'Metadona hidrocloruro', 'Envase con 20 comprimidos', 'Lista I', true),
    ('123987', 'Rubifen 20 mg', 'Metilfenidato hidrocloruro', 'Envase con 30 comprimidos', 'Lista II', true)
ON CONFLICT (codigo_nacional) DO NOTHING;

-- 3. Transacción Inicial de Entrada (Recepción de Lote)
-- Nota: Esta inserción disparará automáticamente el trigger `trg_audit_libro`
INSERT INTO libro_estupefacientes (
    id_producto,
    tipo_movimiento,
    num_lote,
    fecha_caducidad,
    cantidad,
    saldo_resultante,
    doc_referencia,
    prescriptor_destino,
    motivo_ajuste,
    id_usuario_firma,
    id_usuario_aprobacion,
    estado
)
VALUES (
    1, -- Morfina Braun 10 mg/ml
    'ENTRADA',
    'LOT-MB-2026-01',
    '2028-06-30',
    100,
    100,
    'ALB-PROV-99881',
    'Laboratorios Braun S.A.',
    NULL,
    1, -- Firmado por farmacéutico regente
    NULL,
    'CONFIRMADO'
);