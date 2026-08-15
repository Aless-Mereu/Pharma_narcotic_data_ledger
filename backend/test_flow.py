import asyncio
import pyotp
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"
MFA_SECRET = "JBSWY3DPEHPK3PXP"
PASSWORD = "GxPPass2026!"
USERNAME = "farmaceutico_regente"


async def test_storno_flow():
    async with AsyncClient(base_url=BASE_URL) as client:
        # 1. Login
        totp_login = pyotp.TOTP(MFA_SECRET).now()
        login_res = await client.post("/auth/login", json={
            "username": USERNAME,
            "password": PASSWORD,
            "totp_code": totp_login
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Ejecutar Storno sobre el movimiento ID 2 (la salida de 15)
        totp_storno = pyotp.TOTP(MFA_SECRET).now()
        payload_storno = {
            "id_movimiento_original": 2,
            "motivo_ajuste": "Error administrativo en número de receta. Se cancela salida de 15 unidades.",
            "signature_password": PASSWORD,
            "signature_totp": totp_storno
        }

        print("--> Ejecutando Transacción Storno GxP (Anulación del Movimiento #2)...")
        storno_res = await client.post("/ledger/storno", json=payload_storno, headers=headers)

        if storno_res.status_code == 201:
            data = storno_res.json()
            print("\n=======================================================")
            print(" STORNO REGISTRADO Y ASENTADO EN LIBRO OFICIAL")
            print("=======================================================")
            print(f"ID Movimiento Storno: {data['id_movimiento']}")
            print(f"Tipo Movimiento:      {data['tipo_movimiento']}")
            print(f"Cantidad Devuelta:    {data['cantidad']}")
            print(f"Saldo Anterior:       85")
            print(f"Saldo Resultante:     {data['saldo_resultante']} (Saldo esperado: 100)")
            print(f"Doc Referencia:       {data['doc_referencia']}")
            print(f"Timestamp:            {data['timestamp_servidor']}")
            print("=======================================================\n")
        else:
            print(f"[ERROR] Fallo en Storno: {storno_res.status_code} - {storno_res.text}")


if __name__ == "__main__":
    asyncio.run(test_storno_flow())