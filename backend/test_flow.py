import asyncio
import pyotp
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"
MFA_SECRET = "JBSWY3DPEHPK3PXP"
PASSWORD = "GxPPass2026!"
USERNAME = "farmaceutico_regente"

async def test_metrics_and_traceability():
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

        # 2. Resumen Global de Stock
        print("=========================================================================")
        print(" 1. RESUMEN EJECUTIVO DE STOCK Y BALANCES")
        print("=========================================================================")
        res_summary = await client.get("/ledger/metrics/summary", headers=headers)
        for p in res_summary.json():
            print(f"Producto: [{p['codigo_nacional']}] {p['nombre_comercial']} ({p['principio_activo']} - {p.get('presentacion') or p['forma_farmaceutica']})")
            print(f"  - Stock Actual:        {p['stock_actual']} uds")
            print(f"  - Total Entradas:      {p['total_entradas']} uds")
            print(f"  - Total Salidas:       {p['total_salidas']} uds")
            print(f"  - Total Stornos:       {p['total_ajustes_storno']} uds")
            print(f"  - Última Transacción:  {p['ultimo_movimiento']}")

        # 3. Trazabilidad Completa (Quién, Cuándo, Para qué, Hacia dónde)
        print("\n=========================================================================")
        print(" 2. LÍNEA DE VIDA / TRAZABILIDAD REGULATORIA (Producto ID: 1)")
        print("=========================================================================")
        res_trace = await client.get("/ledger/metrics/traceability/1", headers=headers)
        for t in res_trace.json():
            print(f"[{t['timestamp_servidor'][:19]}] Asiento #{t['id_movimiento']}: {t['tipo_movimiento']} ({t['cantidad']} uds) -> Saldo: {t['saldo_resultante']}")
            print(f"  • Firmado por: {t['usuario_firma_nombre']} [{t['usuario_firma_rol']}]")
            print(f"  • Destino/Origen: {t['prescriptor_destino'] or 'N/A'}")
            print(f"  • Doc Ref: {t['doc_referencia']} | Lote: {t['num_lote']}")
            if t['motivo_ajuste']:
                print(f"  • Justificación/Proceso: {t['motivo_ajuste']}")
            print("  " + "-"*65)

if __name__ == "__main__":
    asyncio.run(test_metrics_and_traceability())