# Pharma Narcotic Data Ledger

**Pharma Narcotic Data Ledger** es una aplicación backend orientada a la gestión, trazabilidad e inmutabilidad de movimientos relacionados con estupefacientes en un entorno farmacéutico regulado.

El proyecto está diseñado como una solución técnica inspirada en principios **GxP**, con foco en integridad de datos, auditoría, control de acceso, validaciones de negocio y persistencia segura mediante base de datos relacional.

> Proyecto desarrollado como pieza principal de portfolio, con arquitectura backend moderna, documentación funcional/técnica y validaciones automatizadas.

---

## Tabla de contenidos

- [Visión general](#visión-general)
- [Objetivos del proyecto](#objetivos-del-proyecto)
- [Características principales](#características-principales)
- [Arquitectura](#arquitectura)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Modelo funcional](#modelo-funcional)
- [Seguridad y cumplimiento](#seguridad-y-cumplimiento)
- [Base de datos e inmutabilidad](#base-de-datos-e-inmutabilidad)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Ejecución con Docker](#ejecución-con-docker)
- [Testing](#testing)
- [Documentación incluida](#documentación-incluida)
- [Roadmap](#roadmap)
- [Autor](#autor)

---

## Visión general

En sectores regulados como el farmacéutico, la gestión de sustancias controladas requiere sistemas capaces de garantizar:

- Registro completo de operaciones.
- Trazabilidad extremo a extremo.
- Evidencia de quién hizo qué, cuándo y por qué.
- Restricción de modificaciones no autorizadas.
- Auditoría técnica y funcional.
- Validaciones consistentes y reproducibles.

Este proyecto implementa un **libro digital de movimientos de estupefacientes**, donde cada operación queda registrada de forma persistente y protegida frente a alteraciones posteriores.

---

## Objetivos del proyecto

El objetivo principal de este sistema es demostrar una implementación backend sólida para un caso de uso regulado, combinando buenas prácticas de ingeniería con requisitos cercanos a entornos reales de validación.

### Objetivos técnicos

- Diseñar una API backend clara, modular y mantenible.
- Implementar autenticación y autorización.
- Persistir datos en PostgreSQL mediante SQLAlchemy.
- Aplicar reglas de inmutabilidad a nivel de base de datos.
- Incorporar pruebas automatizadas orientadas a validación GxP.
- Preparar el sistema para ejecución local y contenerizada.
- Documentar requisitos funcionales, arquitectura y modelo técnico.

### Objetivos de producto

- Digitalizar el registro de movimientos de sustancias controladas.
- Reducir riesgo de manipulación de registros críticos.
- Mejorar la trazabilidad de operaciones.
- Facilitar auditorías internas o externas.
- Simular controles habituales en aplicaciones farmacéuticas reguladas.

---

## Características principales

- API backend construida con **FastAPI**.
- Persistencia en **PostgreSQL**.
- Acceso a datos mediante **SQLAlchemy Async**.
- Modelo de dominio orientado a usuarios, productos, movimientos y auditoría.
- Autenticación basada en tokens.
- Reautenticación para operaciones críticas.
- Validaciones de negocio en capa de schemas y servicios.
- Triggers SQL para impedir modificaciones o borrados de registros sensibles.
- Auditoría automática de operaciones.
- Scripts SQL de inicialización de esquema, triggers y datos semilla.
- Tests automatizados para validar flujos críticos.
- Interfaz estática básica para interacción con el sistema.
- Despliegue local mediante Docker Compose.
- Documentación funcional y técnica incluida.

---

## Arquitectura

El proyecto sigue una arquitectura backend modular, separando responsabilidades por capas:### Capas principales

- **API Layer**: definición de endpoints HTTP.
- **Router Layer**: agrupación de rutas por dominio funcional.
- **Schema Layer**: validación y serialización de datos.
- **Domain Model Layer**: representación de entidades persistentes.
- **Security Layer**: autenticación, tokens y verificación de credenciales.
- **Database Layer**: conexión asíncrona y sesiones con PostgreSQL.
- **SQL Control Layer**: DDL, triggers, restricciones e inicialización.

---

## Stack tecnológico

| Área | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Framework API | FastAPI |
| Base de datos | PostgreSQL |
| ORM | SQLAlchemy Async |
| Validación de datos | Pydantic |
| Autenticación | JWT |
| Contenedores | Docker / Docker Compose |
| Testing | Pytest |
| Documentación | Markdown / DOCX |
| Frontend básico | HTML estático |

---

## Estructura del proyecto


````markdown
## Estructura del proyecto


Pharma_narcotic_data_ledger/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── domain.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── ledger.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── ledger.py
│   │   ├── static/
│   │   │   ├── __init__.py
│   │   │   └── index.html
│   │   ├── __init__.py
│   │   └── main.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_gxp_validation.py
│   ├── __init__.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── reset_passwords.py
│   └── test_flow.py
├── database/
│   └── init/
│       ├── 01_schema_ddl.sql
│       ├── 02_triggers_inmutability.sql
│       └── 03_seed_data.sql
├── docs/
│   ├── FDS_Arquitectura_Sistema_Estupefacientes.docx
│   ├── TDS_Modelo_BBDD_Triggers_Estupefacientes.docx
│   └── URS_DIRA_Libro_Estupefacientes.docx
├── conftest.py
├── docker-compose.yml
└── README.md


### Descripción de carpetas principales

| Ruta | Descripción |
|---|---|
| `backend/app/core/` | Configuración, conexión a base de datos y utilidades de seguridad |
| `backend/app/models/` | Modelos de dominio y entidades persistentes |
| `backend/app/routers/` | Endpoints de autenticación y operaciones del ledger |
| `backend/app/schemas/` | Schemas de validación y serialización de datos |
| `backend/app/static/` | Interfaz HTML básica para interacción con la aplicación |
| `backend/tests/` | Tests automatizados de validación funcional y GxP |
| `database/init/` | Scripts SQL de esquema, triggers e inserción de datos iniciales |
| `docs/` | Documentación funcional y técnica del sistema |
````



## Modelo funcional

El sistema está orientado al registro controlado de movimientos asociados a sustancias farmacéuticas sensibles.

Entre los conceptos principales del dominio se encuentran:

- **Usuarios**: actores autenticados que interactúan con el sistema.
- **Productos o sustancias**: elementos sujetos a control y trazabilidad.
- **Movimientos de ledger**: entradas que representan operaciones registradas.
- **Auditoría**: evidencia técnica de acciones realizadas.
- **Validaciones GxP**: controles que aseguran integridad y consistencia.

### Ejemplos de operaciones contempladas

- Inicio de sesión de usuarios.
- Consulta de registros del ledger.
- Alta de movimientos controlados.
- Reautenticación para acciones sensibles.
- Validación de inmutabilidad de registros.
- Verificación de trazabilidad y auditoría.

---

## Seguridad y cumplimiento

El proyecto incorpora varios mecanismos inspirados en buenas prácticas de sistemas regulados:

### Autenticación

El acceso a las funcionalidades principales se protege mediante autenticación basada en tokens.

### Reautenticación

Las operaciones críticas requieren confirmación adicional mediante contraseña, reforzando el principio de responsabilidad individual.

### Integridad de datos

Los registros sensibles se protegen frente a modificaciones posteriores mediante reglas a nivel de base de datos.

### Auditoría

El sistema registra evidencias de operaciones relevantes para facilitar trazabilidad y revisión.

### Separación de responsabilidades

La arquitectura separa configuración, seguridad, modelos, rutas, schemas y scripts SQL, favoreciendo mantenibilidad y revisión técnica.

---

## Base de datos e inmutabilidad

La base de datos se inicializa mediante scripts SQL versionados:### Scripts principales

| Script | Propósito |
|---|---|
| `01_schema_ddl.sql` | Creación del esquema principal de base de datos |
| `02_triggers_inmutability.sql` | Definición de triggers para proteger registros críticos |
| `03_seed_data.sql` | Inserción de datos iniciales para pruebas y demostración |

La inmutabilidad se implementa en la propia base de datos para evitar que la integridad dependa únicamente de la lógica de aplicación.

---

## Instalación y ejecución

### Requisitos previos

- Python 3.12+
- Entorno virtual `virtualenv`
- PostgreSQL
- Docker y Docker Compose, opcional pero recomendado

### 1. Clonar el repositorio### 2. Crear y activar entorno virtual

En Windows:En Linux/macOS:### 3. Instalar dependencias### 4. Configurar variables de entorno

Crea un archivo `.env` o configura las variables necesarias para la conexión a base de datos y seguridad.

Ejemplo:> No incluyas credenciales reales en el repositorio. Usa siempre placeholders o variables de entorno seguras.

### 5. Ejecutar la aplicación

Desde la carpeta del backend:La API quedará disponible en:Documentación interactiva de FastAPI:---

## Ejecución con Docker

El proyecto incluye configuración para levantar los servicios mediante Docker Compose.

Desde la raíz del proyecto:Para detener los servicios:Si quieres eliminar también volúmenes asociados:---

## Testing

El proyecto incluye pruebas automatizadas orientadas a validar aspectos críticos del sistema.

### Ejecutar tests

Desde la raíz del proyecto:O desde el backend:### Áreas cubiertas por los tests

- Flujos funcionales principales.
- Validaciones GxP.
- Trazabilidad de operaciones.
- Restricciones de inmutabilidad.
- Comportamiento esperado ante operaciones no permitidas.

---

## Documentación incluida

El repositorio contiene documentación funcional y técnica en la carpeta `docs/`.### Documentos

| Documento | Descripción |
|---|---|
| `URS_DIRA_Libro_Estupefacientes.docx` | Requisitos de usuario y necesidades funcionales |
| `FDS_Arquitectura_Sistema_Estupefacientes.docx` | Diseño funcional y arquitectura del sistema |
| `TDS_Modelo_BBDD_Triggers_Estupefacientes.docx` | Diseño técnico de base de datos, triggers e inmutabilidad |

Esta documentación refuerza el enfoque profesional del proyecto, mostrando no solo implementación, sino también análisis, diseño y trazabilidad documental.

---

## Roadmap

Próximas mejoras previstas:

- Añadir migraciones con Alembic.
- Incorporar roles y permisos más granulares.
- Implementar firma electrónica avanzada para operaciones críticas.
- Añadir exportación de reportes auditables.
- Mejorar la interfaz web.
- Añadir dashboard de métricas y trazabilidad.
- Integrar observabilidad con logs estructurados.
- Añadir pipeline CI/CD.
- Ampliar cobertura de tests.
- Preparar despliegue cloud.

---

## Valor diferencial del proyecto

Este proyecto destaca dentro de un portfolio porque combina:

- Backend moderno con FastAPI.
- Persistencia robusta en PostgreSQL.
- Diseño orientado a dominios regulados.
- Seguridad y trazabilidad.
- Inmutabilidad aplicada desde base de datos.
- Documentación funcional y técnica.
- Testing de escenarios críticos.
- Preparación para ejecución contenerizada.

No es solo una API CRUD: es una simulación realista de un sistema backend para un contexto farmacéutico regulado.

---

## Autor

Desarrollado por:  **Alessandro García Mereu**.

- GitHub: <https://github.com/Aless-Mereu>
- LinkedIn: [<https://www.linkedin.com/in/alessandro-garc%C3%ADa-mereu-b65224349/>](<URL_DE_TU_LINKEDIN>)


---

## Licencia

Este proyecto se publica con fines educativos y de portfolio.


---

## Nota final

**Pharma Narcotic Data Ledger** representa una aproximación profesional a la construcción de software backend para sectores regulados, priorizando integridad, trazabilidad, seguridad y mantenibilidad.

Es un proyecto pensado para demostrar criterio técnico, capacidad de diseño y comprensión de requisitos exigentes más allá de una implementación básica.