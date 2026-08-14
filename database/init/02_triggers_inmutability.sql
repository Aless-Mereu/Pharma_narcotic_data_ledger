-- Lógica Almacenada en PL/pgSQL para Garantía de Integridad de Datos (ALCOA+)

-- 1. Función para Bloquear UPDATE y DELETE (Regla Append-Only)
CREATE OR REPLACE FUNCTION prevent_update_or_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'VIOLACIÓN DE INTEGRIDAD GxP (Anexo 11): Los registros transaccionales o de auditoría en la tabla % no se pueden modificar ni eliminar. Utilice transacciones de Storno/Anulación.', TG_TABLE_NAME
        USING ERRCODE = 'RESTRICT_VIOLATION';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Asignación de Triggers de Bloqueo a Tablas Críticas
DROP TRIGGER IF EXISTS trg_bloqueo_libro ON libro_estupefacientes;
CREATE TRIGGER trg_bloqueo_libro
BEFORE UPDATE OR DELETE ON libro_estupefacientes
FOR EACH ROW EXECUTE FUNCTION prevent_update_or_delete();

DROP TRIGGER IF EXISTS trg_bloqueo_audit ON audit_trail;
CREATE TRIGGER trg_bloqueo_audit
BEFORE UPDATE OR DELETE ON audit_trail
FOR EACH ROW EXECUTE FUNCTION prevent_update_or_delete();

-- 2. Función para Generación Autónoma de Audit Trail
CREATE OR REPLACE FUNCTION generate_audit_trail()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_trail (
        tabla_afectada,
        operacion,
        id_registro_afectado,
        id_usuario,
        ip_origen,
        timestamp_ntp,
        datos_nuevos
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        NEW.id_movimiento,
        NEW.id_usuario_firma,
        inet_client_addr()::varchar,
        CURRENT_TIMESTAMP,
        to_jsonb(NEW)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Asignación del Trigger de Audit Trail
DROP TRIGGER IF EXISTS trg_audit_libro ON libro_estupefacientes;
CREATE TRIGGER trg_audit_libro
AFTER INSERT ON libro_estupefacientes
FOR EACH ROW EXECUTE FUNCTION generate_audit_trail();