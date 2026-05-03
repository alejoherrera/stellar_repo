"""
anchor_demo.py - PoC: ancla outputs de dIAra en Stellar testnet.

v3: agrega pinning IPFS via Pinata para imagen + JSON canonico.

Implementa el subset minimo de Fase 1 declarada en CONSTITUTION.md:

Por cada output dIAra anclado, una TX con multiples manageData:
  - diara:{id}            -> SHA256(json_canonico) || SHA256(imagen)   (64 bytes, prueba de integridad)
  - diara:{id}:proj       -> codigo de proyecto                        (texto)
  - diara:{id}:dt         -> fecha/hora original del JSON              (texto)
  - diara:{id}:workers    -> cantidad de personas trabajadoras         (texto)
  - diara:{id}:machinery  -> lista de maquinaria, truncada a 64 bytes  (texto)
  - diara:{id}:phase      -> etapa constructiva, truncada a 64 bytes   (texto)
  - diara:{id}:img_cid    -> CID IPFS de la imagen JPG (CIDv1 base32)  (v3)
  - diara:{id}:json_cid   -> CID IPFS del JSON canonico (CIDv1 base32) (v3)

Adicionalmente, una TX de setup del proyecto (one-time) con:
  - proj:{code}:name      -> nombre del proyecto
  - proj:{code}:partner   -> contraparte / cooperante
  - proj:{code}:url       -> URL publica del monitoreo
  - proj:{code}:system    -> sistema productor de los datos (dIAra)

Memo de TX: "dIAra ancla v3" / "dIAra setup v1".

Credenciales:
- Stellar testnet secret: scripts/.env (PoC; en produccion, Secret Manager)
- Pinata JWT: Google Secret Manager (proyecto nifty-province-474317-m0, secret 'pinata-jwt')
  Se cachea en scripts/.env tras el primer fetch via gcloud CLI.

Limitaciones (vs spec Fase 1 completa):
- Sin DB (iteracion siguiente).
- Sin webhook ni firma de dIAra como proveedor.
- Llave testnet en .env (no en Secret Manager aun).
- Sin reconciler.

Uso:
    python scripts/anchor_demo.py --setup-project   # one-time, registra metadatos del proyecto
    python scripts/anchor_demo.py --first           # ancla el primer JSON con IPFS + Stellar
    python scripts/anchor_demo.py --all             # ancla todos (auto-corre setup si falta)

Constitution: cumplimiento parcial de Fase 1; este artefacto no se promueve a mainnet.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from stellar_sdk import Keypair, Network, Server, TransactionBuilder

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPTS_DIR / ".env"

DIARA_DIR = Path(r"C:\Users\aleja\diara_circunvalacion_json")
JSONS_DIR = DIARA_DIR / "json_test_estandarizado"
IMAGES_DIR = DIARA_DIR / "imagenes_tratadas" / "imagenes_tratadas"

NETWORK_PASSPHRASE = Network.TESTNET_NETWORK_PASSPHRASE
HORIZON_URL = "https://horizon-testnet.stellar.org"
EXPLORER_TX_URL = "https://stellar.expert/explorer/testnet/tx/{}"
EXPLORER_ACC_URL = "https://stellar.expert/explorer/testnet/account/{}"

PROJECT_CODE = "circunvalacion-cr"
PROJECT_METADATA = {
    "name": "Monitoreo ciudadano Circunvalacion San Jose",
    "partner": "LanammeUCR",
    "url": "obrapublica.info/ciudadania",
    "system": "dIAra",
}

MEMO_OUTPUT = "dIAra ancla v3"
MEMO_SETUP = "dIAra setup v1"

PINATA_API_BASE = "https://api.pinata.cloud"
PINATA_GATEWAY = "https://gateway.pinata.cloud/ipfs"
GCLOUD_BIN = r"C:\Users\aleja\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
GCP_PROJECT = "nifty-province-474317-m0"
PINATA_JWT_SECRET = "pinata-jwt"


def load_env() -> dict:
    if not ENV_PATH.exists():
        return {}
    out = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def save_env(updates: dict) -> None:
    existing = load_env()
    existing.update(updates)
    lines = [f"{k}={v}" for k, v in existing.items()]
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fetch_pinata_jwt() -> str:
    """Lee Pinata JWT de .env (cache) o de Secret Manager via gcloud CLI."""
    env = load_env()
    cached = env.get("PINATA_JWT")
    if cached:
        return cached
    print(f"[INFO] Fetching Pinata JWT desde Secret Manager (proyecto {GCP_PROJECT})...")
    result = subprocess.run(
        [GCLOUD_BIN, "secrets", "versions", "access", "latest",
         f"--secret={PINATA_JWT_SECRET}", f"--project={GCP_PROJECT}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"gcloud secrets access fallo: {result.stderr}")
    jwt = result.stdout.strip()
    if not jwt:
        raise RuntimeError("Pinata JWT vacio desde Secret Manager")
    save_env({"PINATA_JWT": jwt})
    print("[OK] Pinata JWT cacheada en scripts/.env (gitignored)")
    return jwt


def pinata_pin_file(jwt: str, file_path: Path, name: str, keyvalues: dict) -> str:
    """Pinea un archivo en IPFS via Pinata. Retorna CID v1 base32."""
    headers = {"Authorization": f"Bearer {jwt}"}
    metadata = {"name": name, "keyvalues": keyvalues}
    options = {"cidVersion": 1}
    with file_path.open("rb") as fh:
        files = {
            "file": (file_path.name, fh, "application/octet-stream"),
            "pinataMetadata": (None, json.dumps(metadata), "application/json"),
            "pinataOptions": (None, json.dumps(options), "application/json"),
        }
        r = requests.post(f"{PINATA_API_BASE}/pinning/pinFileToIPFS",
                          headers=headers, files=files, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"Pinata pinFileToIPFS fallo {r.status_code}: {r.text}")
    return r.json()["IpfsHash"]


def pinata_pin_json(jwt: str, obj, name: str, keyvalues: dict) -> str:
    """Pinea un JSON en IPFS via Pinata. Retorna CID v1 base32."""
    headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}
    body = {
        "pinataContent": obj,
        "pinataMetadata": {"name": name, "keyvalues": keyvalues},
        "pinataOptions": {"cidVersion": 1},
    }
    r = requests.post(f"{PINATA_API_BASE}/pinning/pinJSONToIPFS",
                      headers=headers, json=body, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Pinata pinJSONToIPFS fallo {r.status_code}: {r.text}")
    return r.json()["IpfsHash"]


def get_or_create_keypair() -> Keypair:
    env = load_env()
    secret = env.get("STELLAR_TESTNET_SECRET") or os.environ.get("STELLAR_TESTNET_SECRET")
    if secret:
        kp = Keypair.from_secret(secret)
        print(f"[OK] Llave existente cargada: {kp.public_key}")
        return kp

    kp = Keypair.random()
    print(f"[INFO] Llave testnet generada: {kp.public_key}")
    print(f"[INFO] Fondeando via friendbot...")
    r = requests.get(f"https://friendbot.stellar.org?addr={kp.public_key}", timeout=60)
    r.raise_for_status()
    print(f"[OK] Cuenta fondeada con XLM testnet")
    print(f"[OK] Explorer cuenta: {EXPLORER_ACC_URL.format(kp.public_key)}")
    save_env({"STELLAR_TESTNET_SECRET": kp.secret, "STELLAR_TESTNET_PUBLIC": kp.public_key})
    print(f"[OK] Secret guardado en {ENV_PATH} (gitignored)")
    return kp


def canonical_json_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def find_image(json_filename: str):
    base = json_filename.replace(".json", "")
    date = base.split("-")[0]
    img_path = IMAGES_DIR / date / f"{base}.jpg"
    return img_path if img_path.exists() else None


def truncate_utf8(s: str, max_bytes: int) -> bytes:
    enc = s.encode("utf-8")
    if len(enc) <= max_bytes:
        return enc
    while len(enc) > max_bytes:
        s = s[:-1]
        enc = s.encode("utf-8")
    return enc


def add_data_op(builder: TransactionBuilder, key: str, value_bytes: bytes) -> None:
    if len(key.encode("utf-8")) > 64:
        raise ValueError(f"Key excede 64 bytes: {key!r}")
    if len(value_bytes) > 64:
        value_bytes = value_bytes[:64]
    builder.append_manage_data_op(data_name=key, data_value=value_bytes if value_bytes else b" ")


def project_setup_exists(server: Server, public_key: str) -> bool:
    try:
        acc = server.accounts().account_id(public_key).call()
        data = acc.get("data", {})
        return f"proj:{PROJECT_CODE}:name" in data
    except Exception:
        return False


def anchor_setup(server: Server, kp: Keypair) -> dict:
    print(f"\n--- Setup proyecto: {PROJECT_CODE} ---")
    account = server.load_account(kp.public_key)
    builder = (
        TransactionBuilder(
            source_account=account,
            network_passphrase=NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .add_text_memo(MEMO_SETUP)
        .set_timeout(60)
    )
    for k, v in PROJECT_METADATA.items():
        add_data_op(builder, f"proj:{PROJECT_CODE}:{k}", truncate_utf8(v, 64))

    tx = builder.build()
    tx.sign(kp)
    response = server.submit_transaction(tx)
    tx_hash = response.get("hash")
    ledger = response.get("ledger")
    print(f"[OK] Setup TX hash: {tx_hash}")
    print(f"[OK] Explorer: {EXPLORER_TX_URL.format(tx_hash)}")
    return {
        "type": "project_setup",
        "project_code": PROJECT_CODE,
        "metadata": PROJECT_METADATA,
        "tx_hash": tx_hash,
        "ledger": ledger,
        "explorer_url": EXPLORER_TX_URL.format(tx_hash),
        "anchored_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def anchor_one(server: Server, kp: Keypair, jwt: str, json_path: Path) -> dict:
    print(f"\n--- Procesando {json_path.name} ---")

    with json_path.open("r", encoding="utf-8") as f:
        diara_output = json.load(f)
    json_canonical = canonical_json_bytes(diara_output)
    json_hash = sha256_bytes(json_canonical)
    print(f"[OK] Hash JSON canonico: {json_hash.hex()}")

    img_path = find_image(json_path.name)
    if img_path:
        with img_path.open("rb") as f:
            img_hash = sha256_bytes(f.read())
        print(f"[OK] Imagen local: {img_path.name}, hash: {img_hash.hex()}")
    else:
        img_hash = b"\x00" * 32
        print(f"[WARN] Imagen no encontrada para {json_path.name}; usando 32 bytes en cero")

    output_id = json_path.stem
    base_key = f"diara:{output_id}"

    pin_keyvalues = {
        "project": PROJECT_CODE,
        "output_id": output_id,
        "system": "dIAra",
    }

    if img_path:
        print(f"[INFO] Pineando imagen en IPFS via Pinata...")
        img_cid = pinata_pin_file(jwt, img_path, f"{output_id}.jpg",
                                  {**pin_keyvalues, "type": "image"})
        print(f"[OK] Image CID: {img_cid}")
        print(f"[OK] Image gateway: {PINATA_GATEWAY}/{img_cid}")
    else:
        img_cid = ""

    print(f"[INFO] Pineando JSON canonico en IPFS via Pinata...")
    json_cid = pinata_pin_json(jwt, diara_output, f"{output_id}.json",
                                {**pin_keyvalues, "type": "json"})
    print(f"[OK] JSON CID: {json_cid}")
    print(f"[OK] JSON gateway: {PINATA_GATEWAY}/{json_cid}")

    workers = str(diara_output.get("personas_trabajadoras", 0))
    machinery_list = diara_output.get("maquinaria") or []
    machinery_str = ", ".join(machinery_list) if machinery_list else "ninguna"
    phase = diara_output.get("etapa_constructiva", "") or ""
    fecha = diara_output.get("fecha_hora", "") or ""

    print(f"[INFO] Metadatos: workers={workers}, machinery={machinery_str!r}, phase={phase!r}")

    account = server.load_account(kp.public_key)
    builder = (
        TransactionBuilder(
            source_account=account,
            network_passphrase=NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .add_text_memo(MEMO_OUTPUT)
        .set_timeout(60)
    )

    add_data_op(builder, base_key, json_hash + img_hash)
    add_data_op(builder, f"{base_key}:proj", PROJECT_CODE.encode("utf-8"))
    add_data_op(builder, f"{base_key}:dt", truncate_utf8(fecha, 64))
    add_data_op(builder, f"{base_key}:workers", workers.encode("utf-8"))
    add_data_op(builder, f"{base_key}:machinery", truncate_utf8(machinery_str, 64))
    add_data_op(builder, f"{base_key}:phase", truncate_utf8(phase, 64))
    if img_cid:
        add_data_op(builder, f"{base_key}:img_cid", img_cid.encode("utf-8"))
    add_data_op(builder, f"{base_key}:json_cid", json_cid.encode("utf-8"))

    tx = builder.build()
    tx.sign(kp)
    response = server.submit_transaction(tx)

    tx_hash = response.get("hash")
    ledger = response.get("ledger")
    print(f"[OK] TX submitted, hash={tx_hash}, ledger={ledger}")
    print(f"[OK] Explorer: {EXPLORER_TX_URL.format(tx_hash)}")

    return {
        "output_id": output_id,
        "project_code": PROJECT_CODE,
        "json_file": json_path.name,
        "image_file": img_path.name if img_path else None,
        "json_hash_hex": json_hash.hex(),
        "image_hash_hex": img_hash.hex(),
        "ipfs": {
            "image_cid": img_cid,
            "json_cid": json_cid,
            "image_gateway": f"{PINATA_GATEWAY}/{img_cid}" if img_cid else None,
            "json_gateway": f"{PINATA_GATEWAY}/{json_cid}",
        },
        "metadata_on_chain": {
            "datetime": fecha,
            "workers": workers,
            "machinery": machinery_str,
            "phase": phase,
        },
        "tx_hash": tx_hash,
        "ledger": ledger,
        "explorer_url": EXPLORER_TX_URL.format(tx_hash),
        "anchored_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="Ancla outputs de dIAra en Stellar testnet (PoC Fase 1, v2)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--setup-project", action="store_true", help="One-time: registra metadatos del proyecto on-chain")
    group.add_argument("--first", action="store_true", help="Ancla solo el primer JSON disponible")
    group.add_argument("--all", action="store_true", help="Ancla todos los JSONs estandarizados")
    args = parser.parse_args()

    if not JSONS_DIR.exists():
        print(f"[ERROR] No se encontro {JSONS_DIR}")
        sys.exit(1)

    kp = get_or_create_keypair()
    server = Server(HORIZON_URL)
    results = []

    if args.setup_project:
        results.append(anchor_setup(server, kp))
    else:
        if not project_setup_exists(server, kp.public_key):
            print("[INFO] Setup del proyecto no detectado on-chain; ejecutando setup primero...")
            results.append(anchor_setup(server, kp))
        else:
            print(f"[OK] Setup del proyecto ya existe on-chain para {PROJECT_CODE}")

        json_files = sorted(p for p in JSONS_DIR.glob("*.json") if not p.name.startswith("_"))
        if not json_files:
            print(f"[ERROR] No hay JSONs en {JSONS_DIR}")
            sys.exit(1)
        if args.first:
            json_files = [json_files[0]]

        jwt = fetch_pinata_jwt()
        print(f"[INFO] Anclando {len(json_files)} output(s) en Stellar testnet con IPFS pinning")
        for jf in json_files:
            try:
                results.append(anchor_one(server, kp, jwt, jf))
            except Exception as exc:
                print(f"[ERROR] Fallo al anclar {jf.name}: {exc!r}")
                results.append({"output_id": jf.stem, "error": repr(exc)})

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = SCRIPTS_DIR / f"anchors_log_{ts}.json"
    with log_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "anchored_by": kp.public_key,
                "network": "testnet",
                "project_code": PROJECT_CODE,
                "results": results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"\n[OK] Log guardado: {log_path}")

    ok = sum(1 for r in results if "tx_hash" in r)
    print(f"[RESUMEN] {ok}/{len(results)} TX exitosas")


if __name__ == "__main__":
    main()
