import pytest
import pyotp
import psycopg2
from psycopg2 import errors

MFA_SECRET = "JBSWY3DPEHPK3PXP"
PASSWORD = "GxPPass2026!"
USERNAME = "farmaceutico_regente"
SYNC_DB_URI = "postgresql://gxp_admin:SecuReGxP2026!@localhost:5432/pharma_narcotics_db"


@pytest.fixture
def auth_credentials():
    return {"secret": MFA_SECRET, "password": PASSWORD, "username": USERNAME}


@pytest.mark.asyncio
async def test_01_login_mfa_success(client, auth_credentials):
    totp_code = pyotp.TOTP(auth_credentials["secret"]).now()
    res = await client.post("/auth/login", json={
        "username": auth_credentials["username"],
        "password": auth_credentials["password"],
        "totp_code": totp_code
    })
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert res.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_02_signature_rejection_wrong_credentials(client, auth_credentials):
    totp_login = pyotp.TOTP(auth_credentials["secret"]).now()
    login_res = await client.post("/auth/login", json={
        "username": auth_credentials["username"],
        "password": auth_credentials["password"],
        "totp_code": totp_login
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    totp_sig = pyotp.TOTP(auth_credentials["secret"]).now()
    res = await client.post("/ledger/movement", headers=headers, json={
        "id_producto": 1,
        "tipo_movimiento": "SALIDA",
        "num_lote": "LOT-MB-2026-01",
        "fecha_caducidad": "2028-06-30",
        "cantidad": 5,
        "doc_referencia": "REC-TEST-FAIL",
        "signature_password": "WrongPassword123!",
        "signature_totp": totp_sig
    })
    assert res.status_code == 401
    assert "Firma rechazada: Contraseña incorrecta" in res.json()["detail"]


@pytest.mark.asyncio
async def test_03_stock_underflow_prevention(client, auth_credentials):
    totp_login = pyotp.TOTP(auth_credentials["secret"]).now()
    login_res = await client.post("/auth/login", json={
        "username": auth_credentials["username"],
        "password": auth_credentials["password"],
        "totp_code": totp_login
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    totp_sig = pyotp.TOTP(auth_credentials["secret"]).now()
    res = await client.post("/ledger/movement", headers=headers, json={
        "id_producto": 1,
        "tipo_movimiento": "SALIDA",
        "num_lote": "LOT-MB-2026-01",
        "fecha_caducidad": "2028-06-30",
        "cantidad": 99999,
        "doc_referencia": "REC-TEST-UNDERFLOW",
        "signature_password": auth_credentials["password"],
        "signature_totp": totp_sig
    })
    assert res.status_code == 400
    assert "Saldo insuficiente" in res.json()["detail"]


import subprocess


def test_04_database_immutability_trigger():
    """Valida que el trigger de PostgreSQL bloquea cualquier intento de UPDATE directo."""
    cmd = [
        "docker", "compose", "exec", "-T", "db",
        "psql", "-U", "gxp_admin", "-d", "pharma_narcotics_db",
        "-c", "UPDATE libro_estupefacientes SET cantidad = 999 WHERE id_movimiento = 1;"
    ]

    # errors="replace" previene fallos por bytes especiales de codificación en consola
    result = subprocess.run(cmd, capture_output=True, text=True, errors="replace")

    # La ejecución debe fallar con código de error!= 0 y mensaje del trigger
    assert result.returncode != 0, "El trigger debió rechazar la sentencia UPDATE"
    output = result.stderr + result.stdout
    assert "INTEGRIDAD GxP" in output or "prohibid" in output or "ERROR" in output