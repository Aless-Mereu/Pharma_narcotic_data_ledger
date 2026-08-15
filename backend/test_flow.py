import asyncio
import pyotp
from datetime import date
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"
MFA_SECRET = "JBSWY3DPEHPK3PXP"
PASSWORD = "GxPPass2026!"
USERNAME = "farmaceutico_regente"


async def test_complete_gxp_flow():
    async with AsyncClient(base_url=BASE_URL) as client:
        # 1. Obtener código TOTP para Login
        totp_login = pyotp.TOTP(MFA_SECRET).now()

        print("--> 1. Ejecutando Login con MFA...")
        login_res = await client.post("/auth/login", json={
            "username": USERNAME,
            "password": PASSWORD,
            "totp_code": totp_login
        })

        if login_res.status_code != 200:
            print(f"[ERROR] Fallo en Login: {login_res.status_code} - {login_res.text}")
            return

        token = login_res.json()["access_token"]
        print(f"[OK] Token JWT obtenido: {token[:25]}...")

        # 2. Generar TOTP fresco para Re-Autenticación (Firma GxP)
        totp_signature = pyotp.TOTP(MFA_SECRET).now()
        headers = {"Authorization": f"Bearer {token}"}

        payload_movimiento = {
            "id_producto": 1,
            "tipo_movimiento": "SALIDA",
            "num_lote": "LOT-MB-2026-01",
            "fecha_caducidad": "2028-06-30",
            "cantidad": 15,
            "doc_referencia": "REC-OFICIAL-2026-0001",
            "prescriptor_destino": "Hospital General - Unidad Dolor",
            "motivo_ajuste": None,
            "signature_password": PASSWORD,
            "signature_totp": totp_signature
        }

        print("--> 2. Firmando y registrando movimiento GxP (Dispensación)...")
        movement_res = await client.post("/ledger/movement", json=payload_movimiento, headers=headers)

        if movement_res.status_code == 201:
            data = movement_res.json()
            print("\n=======================================================")
            print(" TRANSACCIÓN REGISTRADA Y FIRMADA CORRECTAMENTE")
            print("=======================================================")
            print(f"ID Movimiento:    {data['id_movimiento']}")
            print(f"Tipo Movimiento:  {data['tipo_movimiento']}")
            print(f"Cantidad:         {data['cantidad']}")
            print(f"Saldo Anterior:   100")
            print(f"Saldo Resultante: {data['saldo_resultante']} (Saldo esperado: 85)")
            print(f"Timestamp:        {data['timestamp_servidor']}")
            print("=======================================================\n")
        else:
            print(f"[ERROR] Fallo en registro de movimiento: {movement_res.status_code} - {movement_res.text}")


if __name__ == "__main__":
    # Requiere httpx (pip install httpx)
    asyncio.run(test_complete_gxp_flow())