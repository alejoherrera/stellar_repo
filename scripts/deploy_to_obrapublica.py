"""
deploy_to_obrapublica.py - Despliega el viewer dIAra×Stellar a obrapublica.info/stellar.

Pasos:
  1. Lee PA token desde Google Secret Manager (proyecto nifty-province-474317-m0,
     secret 'pythonanywhere-token').
  2. Sube viewer/deploy/stellar.html a /home/alejocr/diara/templates/stellar.html.
  3. Lee /home/alejocr/diara/app.py de PA, agrega route /stellar si no existe
     (idempotente), sube de vuelta.
  4. Reload del webapp www.obrapublica.info.
  5. Test HTTP 200 en https://www.obrapublica.info/stellar.

Uso:
    python scripts/deploy_to_obrapublica.py
"""
import subprocess
import sys
from pathlib import Path

import requests

GCLOUD_BIN = r"C:\Users\aleja\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
GCP_PROJECT = "nifty-province-474317-m0"
PA_TOKEN_SECRET = "pythonanywhere-token"

PA_USER = "alejocr"
PA_DOMAIN = "www.obrapublica.info"
PA_BASE = f"https://www.pythonanywhere.com/api/v0/user/{PA_USER}"

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_HTML = REPO_ROOT / "viewer" / "deploy" / "stellar.html"
LOCAL_DEV_HTML = REPO_ROOT / "viewer" / "deploy" / "stellar_dev.html"
LOCAL_TIMELAPSE_HTML = REPO_ROOT / "viewer" / "deploy" / "stellar_timelapse.html"
LOCAL_JS_SDK = REPO_ROOT / "sdk" / "js" / "monitor-as-a-service.js"

REMOTE_HTML = "/home/alejocr/diara/templates/stellar.html"
REMOTE_DEV_HTML = "/home/alejocr/diara/templates/stellar_dev.html"
REMOTE_TIMELAPSE_HTML = "/home/alejocr/diara/templates/stellar_timelapse.html"
REMOTE_JS_SDK = "/home/alejocr/diara/static/monitor-as-a-service.js"
REMOTE_APP_PY = "/home/alejocr/diara/app.py"

ROUTE_MARKER = "@app.route('/stellar')"
DEV_ROUTE_MARKER = "@app.route('/stellar/dev')"
TIMELAPSE_ROUTE_MARKER = "@app.route('/stellar/timelapse')"
ROUTE_BLOCK = """
# ========== STELLAR VIEWER ROUTES (hackathon 2026) ==========
@app.route('/stellar')
def stellar():
    \"\"\"Viewer de anclas MaaS en Stellar testnet + IPFS\"\"\"
    logger.debug("Ruta /stellar accedida")
    return render_template('stellar.html')

@app.route('/stellar/dev')
def stellar_dev():
    \"\"\"Developer hub: schema spec, SDKs, quickstart para terceros que construyen sobre MaaS.\"\"\"
    logger.debug("Ruta /stellar/dev accedida")
    return render_template('stellar_dev.html')
# ============================================================

"""


def fetch_pa_token() -> str:
    print(f"[INFO] Recuperando PA token desde Secret Manager ({GCP_PROJECT}/{PA_TOKEN_SECRET})...")
    result = subprocess.run(
        [GCLOUD_BIN, "secrets", "versions", "access", "latest",
         f"--secret={PA_TOKEN_SECRET}", f"--project={GCP_PROJECT}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"gcloud secrets access fallo: {result.stderr.strip()}")
    token = result.stdout.strip()
    if not token:
        raise RuntimeError("PA token vacio")
    print(f"[OK] PA token recuperado (longitud {len(token)})")
    return token


def pa_upload_file(token: str, remote_path: str, content_bytes: bytes, label: str):
    print(f"[INFO] Subiendo {label} -> {remote_path} ({len(content_bytes)} bytes)")
    headers = {"Authorization": f"Token {token}"}
    files = {"content": ("file", content_bytes, "application/octet-stream")}
    url = f"{PA_BASE}/files/path{remote_path}"
    r = requests.post(url, headers=headers, files=files, timeout=60)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Upload fallo {r.status_code}: {r.text[:300]}")
    print(f"[OK] Upload {label}: HTTP {r.status_code}")


def pa_read_file(token: str, remote_path: str) -> str:
    headers = {"Authorization": f"Token {token}"}
    url = f"{PA_BASE}/files/path{remote_path}"
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Read {remote_path} fallo {r.status_code}: {r.text[:200]}")
    return r.text


def pa_reload_webapp(token: str):
    print(f"[INFO] Reloading webapp {PA_DOMAIN}...")
    headers = {"Authorization": f"Token {token}"}
    url = f"{PA_BASE}/webapps/{PA_DOMAIN}/reload/"
    r = requests.post(url, headers=headers, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Reload fallo {r.status_code}: {r.text[:300]}")
    print(f"[OK] Reload disparado, HTTP {r.status_code}")


def patch_app_py(content: str) -> tuple[str, bool]:
    """Inserta rutas faltantes antes del bloque blockchain o antes del if __name__.
    Idempotente: si todas las rutas ya existen, no hace nada.
    Retorna (nuevo_contenido, modificado)."""
    has_stellar = ROUTE_MARKER in content
    has_dev = DEV_ROUTE_MARKER in content
    has_timelapse = TIMELAPSE_ROUTE_MARKER in content
    if has_stellar and has_dev and has_timelapse:
        return content, False

    # Construir bloques individuales solo para las rutas que faltan
    blocks = []
    if not has_dev:
        blocks.append("""
@app.route('/stellar/dev')
def stellar_dev():
    \"\"\"Developer hub: schema spec, SDKs, quickstart para terceros que construyen sobre MaaS.\"\"\"
    logger.debug("Ruta /stellar/dev accedida")
    return render_template('stellar_dev.html')
""")
    if not has_timelapse:
        blocks.append("""
@app.route('/stellar/timelapse')
def stellar_timelapse():
    \"\"\"Sample app: timelapse animado de outputs anclados, demuestra reusabilidad del SDK.\"\"\"
    logger.debug("Ruta /stellar/timelapse accedida")
    return render_template('stellar_timelapse.html')
""")

    additions = "".join(blocks)
    blockchain_marker = "# ========== BLOCKCHAIN INTEGRATION =========="
    if blockchain_marker in content:
        return content.replace(blockchain_marker, additions + "\n" + blockchain_marker, 1), True
    return content.rstrip() + "\n" + additions, True

    # Preferencia: insertar antes del bloque blockchain
    blockchain_marker = "# ========== BLOCKCHAIN INTEGRATION =========="
    if blockchain_marker in content:
        new = content.replace(blockchain_marker, ROUTE_BLOCK + blockchain_marker, 1)
        return new, True

    # Fallback: insertar antes de if __name__
    main_marker = "if __name__ == '__main__':"
    if main_marker in content:
        new = content.replace(main_marker, ROUTE_BLOCK + main_marker, 1)
        return new, True

    # Ultimo fallback: append al final
    return content.rstrip() + "\n\n" + ROUTE_BLOCK, True


def main():
    if not LOCAL_HTML.exists():
        print(f"[ERROR] No existe {LOCAL_HTML}")
        sys.exit(1)

    token = fetch_pa_token()

    # Paso 1: subir stellar.html (viewer)
    html_bytes = LOCAL_HTML.read_bytes()
    pa_upload_file(token, REMOTE_HTML, html_bytes, "stellar.html")

    # Paso 1b: subir stellar_dev.html (dev hub)
    if LOCAL_DEV_HTML.exists():
        pa_upload_file(token, REMOTE_DEV_HTML, LOCAL_DEV_HTML.read_bytes(), "stellar_dev.html")

    # Paso 1c: subir stellar_timelapse.html (sample app)
    if LOCAL_TIMELAPSE_HTML.exists():
        pa_upload_file(token, REMOTE_TIMELAPSE_HTML, LOCAL_TIMELAPSE_HTML.read_bytes(), "stellar_timelapse.html")

    # Paso 1d: subir SDK JS como static asset (para que devs lo importen via CDN)
    if LOCAL_JS_SDK.exists():
        pa_upload_file(token, REMOTE_JS_SDK, LOCAL_JS_SDK.read_bytes(), "monitor-as-a-service.js")

    # Paso 2: leer y patchar app.py
    print(f"[INFO] Leyendo {REMOTE_APP_PY}...")
    current_app_py = pa_read_file(token, REMOTE_APP_PY)
    print(f"[OK] app.py actual: {len(current_app_py)} chars")

    new_app_py, modified = patch_app_py(current_app_py)
    if not modified:
        print(f"[OK] Route /stellar ya existe en app.py, no se modifica")
    else:
        # Verificar que el resultado solo agrega contenido (R0)
        if len(new_app_py) <= len(current_app_py):
            raise RuntimeError("Patch resulto en contenido mas corto, abortando")
        diff = len(new_app_py) - len(current_app_py)
        print(f"[INFO] app.py crece {diff} chars con la route /stellar")
        pa_upload_file(token, REMOTE_APP_PY, new_app_py.encode("utf-8"), "app.py (parcheado)")

    # Paso 3: reload
    pa_reload_webapp(token)

    # Paso 4: test final (con un poco de espera)
    import time
    print("[INFO] Esperando 8s para que el webapp termine de recargar...")
    time.sleep(8)
    test_url = f"https://{PA_DOMAIN}/stellar"
    print(f"[INFO] Probando {test_url}")
    r = requests.get(test_url, timeout=30, allow_redirects=True)
    print(f"[RESULT] HTTP {r.status_code}, content-length={len(r.content)}")
    if r.status_code == 200 and "Monitoreo" in r.text and "stellar.expert" in r.text:
        print(f"[OK] Deploy exitoso! Abrir: {test_url}")
    else:
        print(f"[WARN] Status inesperado o contenido no esperado. Inspeccionar manualmente.")
        print(f"       Primeros 200 chars: {r.text[:200]!r}")


if __name__ == "__main__":
    main()
