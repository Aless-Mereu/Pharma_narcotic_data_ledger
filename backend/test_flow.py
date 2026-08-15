import asyncio
import pyotp
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"
MFA_SECRET = "JBSWY3DPEHPK3PXP"
PASSWORD = "GxPPass2026!"
USERNAME = "farmaceutico_regente"

async def test_ledger_reporting():
    async with AsyncClient(base_url=BASE_URL) as client:
        # 1. Login
        totp = pyotp.TOTP(MFA_SECRET).now()
        login_res = await client.post("/auth/login", json={
            "username": USERNAME,
            "password": PASSWORD,
            "totp_code": totp
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Consultar Libro Oficial del Producto 1
        print("--> 1. Consultando Libro Oficial Diligenciado (Producto 1)...")
        ledger_res = await client.get("/ledger/book/1", headers=headers)
        entries = ledger_res.json()
        print(f"[OK] Total asientos recuperados: {len(entries)}")
        for e in entries:
            print(f"  [Asiento #{e['id_movimiento']}] Tipo: {e['tipo_movimiento']:<14} Cant: {e['cantidad']:<4} Saldo: {e['saldo_resultante']:<4} Ref: {e['doc_referencia']}")

        # 3. Consultar Audit Trail
        print("\n--> 2. Consultando Audit Trail Inmutable...")
        audit_res = await client.get("/ledger/audit-trail?limit=5", headers=headers)
        trails = audit_res.json()
        print(f"[OK] Total registros audit recuperados: {len(trails)}")
        for t in trails:
            print(f"  [Audit #{t['id_audit']}] Tabla: {t['tabla_afectada']:<20} Op: {t['operacion']:<6} Fecha NTP: {t['timestamp_ntp']}")

        # 4. Descargar Exportación Oficial CSV
        print("\n--> 3. Descargando Exportación CSV Oficial...")
        csv_res = await client.get("/ledger/export/csv/1", headers=headers)
        print(f"[OK] Código {csv_res.status_code} - Tamaño CSV: {len(csv_res.text)} bytes")
        print("Vista previa del CSV:")
        for line in csv_res.text.strip().split("\n")[:4]:
            print(f"  {line}")

if __name__ == "__main__":
    asyncio.run(test_ledger_reporting())