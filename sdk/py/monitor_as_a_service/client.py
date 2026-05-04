"""Client for reading MaaS Open Schema v1 anchors from Stellar + IPFS."""
from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field
from typing import Iterator

import requests

DEFAULT_HORIZONS = {
    "testnet": "https://horizon-testnet.stellar.org",
    "public": "https://horizon.stellar.org",
}

DEFAULT_GATEWAYS = (
    "https://gateway.pinata.cloud/ipfs/",
    "https://ipfs.io/ipfs/",
    "https://dweb.link/ipfs/",
    "https://4everland.io/ipfs/",
)


def canonical_json_bytes(obj) -> bytes:
    """Encode obj as canonical JSON per MaaS Open Schema section 4."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


@dataclass
class Project:
    code: str
    name: str | None = None
    partner: str | None = None
    url: str | None = None
    system: str | None = None


@dataclass
class Output:
    output_id: str
    project_code: str | None = None
    datetime: str | None = None
    workers: int | None = None
    machinery: str | None = None
    phase: str | None = None
    json_cid: str | None = None
    image_cid: str | None = None
    json_hash_onchain: str | None = None
    image_hash_onchain: str | None = None

    @property
    def json_url(self) -> str | None:
        return f"https://gateway.pinata.cloud/ipfs/{self.json_cid}" if self.json_cid else None

    @property
    def image_url(self) -> str | None:
        return f"https://gateway.pinata.cloud/ipfs/{self.image_cid}" if self.image_cid else None


@dataclass
class VerificationResult:
    output_id: str
    json_ok: bool | None = None
    image_ok: bool | None = None
    computed_json_hash: str | None = None
    computed_image_hash: str | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def all_ok(self) -> bool:
        return bool(self.json_ok) and (self.image_ok is None or self.image_ok)


class Client:
    """Read-only client for a MaaS publisher account."""

    def __init__(
        self,
        account: str,
        horizon: str = DEFAULT_HORIZONS["testnet"],
        gateways: tuple[str, ...] = DEFAULT_GATEWAYS,
        timeout: int = 30,
    ):
        self.account = account
        self.horizon = horizon.rstrip("/")
        self.gateways = gateways
        self.timeout = timeout
        self._raw_data: dict | None = None

    @classmethod
    def testnet(cls, account: str, **kw) -> "Client":
        return cls(account, horizon=DEFAULT_HORIZONS["testnet"], **kw)

    @classmethod
    def mainnet(cls, account: str, **kw) -> "Client":
        return cls(account, horizon=DEFAULT_HORIZONS["public"], **kw)

    def fetch_raw(self, force: bool = False) -> dict:
        """Fetch the account JSON from Horizon. Cached unless force=True."""
        if self._raw_data is not None and not force:
            return self._raw_data
        r = requests.get(f"{self.horizon}/accounts/{self.account}", timeout=self.timeout)
        r.raise_for_status()
        self._raw_data = r.json()
        return self._raw_data

    def project(self) -> Project | None:
        """Return the project metadata (None if no project setup TX found)."""
        data = self.fetch_raw().get("data", {})
        proj_code = None
        fields: dict[str, str] = {}
        for key, b64val in data.items():
            if not key.startswith("proj:"):
                continue
            rest = key[len("proj:"):]
            parts = rest.split(":", 1)
            if len(parts) != 2:
                continue
            code, field_name = parts
            proj_code = code
            fields[field_name] = base64.b64decode(b64val).decode("utf-8", errors="replace")
        if not proj_code:
            return None
        return Project(code=proj_code, **{k: v for k, v in fields.items() if k in {"name", "partner", "url", "system"}})

    def outputs(self) -> Iterator[Output]:
        """Yield all outputs anchored on this account, sorted by output_id desc (newest first)."""
        data = self.fetch_raw().get("data", {})
        agg: dict[str, dict] = {}
        for key, b64val in data.items():
            if not key.startswith("diara:"):
                continue
            rest = key[len("diara:"):]
            parts = rest.split(":")
            oid = parts[0]
            field_name = parts[1] if len(parts) > 1 else "_hash"
            agg.setdefault(oid, {})
            raw = base64.b64decode(b64val)
            agg[oid][field_name] = raw

        for oid in sorted(agg.keys(), reverse=True):
            fields = agg[oid]
            hash_blob: bytes = fields.get("_hash", b"")
            json_hash = hash_blob[:32].hex() if len(hash_blob) >= 32 else None
            image_hash = hash_blob[32:64].hex() if len(hash_blob) >= 64 else None
            workers_raw = fields.get("workers", b"").decode("utf-8", errors="replace")
            try:
                workers = int(workers_raw) if workers_raw else None
            except ValueError:
                workers = None
            yield Output(
                output_id=oid,
                project_code=fields.get("proj", b"").decode("utf-8", errors="replace") or None,
                datetime=fields.get("dt", b"").decode("utf-8", errors="replace") or None,
                workers=workers,
                machinery=fields.get("machinery", b"").decode("utf-8", errors="replace") or None,
                phase=fields.get("phase", b"").decode("utf-8", errors="replace") or None,
                json_cid=fields.get("json_cid", b"").decode("utf-8", errors="replace") or None,
                image_cid=fields.get("img_cid", b"").decode("utf-8", errors="replace") or None,
                json_hash_onchain=json_hash,
                image_hash_onchain=image_hash,
            )

    def get(self, output_id: str) -> Output | None:
        for o in self.outputs():
            if o.output_id == output_id:
                return o
        return None

    def fetch_from_ipfs(self, cid: str, as_bytes: bool = False):
        """Try each gateway in order until one returns 2xx. Returns parsed JSON or raw bytes."""
        last_err = None
        for gw in self.gateways:
            try:
                r = requests.get(gw + cid, timeout=self.timeout)
                if not r.ok:
                    last_err = f"{gw}: HTTP {r.status_code}"
                    continue
                return r.content if as_bytes else r.json()
            except Exception as exc:  # noqa: BLE001
                last_err = f"{gw}: {exc}"
        raise RuntimeError(f"All IPFS gateways failed: {last_err}")

    def verify(self, output_id: str, verify_image: bool = True) -> VerificationResult:
        """Fetch content from IPFS and compare hashes against on-chain anchors."""
        o = self.get(output_id)
        if not o:
            return VerificationResult(output_id=output_id, errors=["output not found"])
        result = VerificationResult(output_id=output_id)

        if not o.json_cid:
            result.errors.append("no json_cid anchored")
        else:
            try:
                obj = self.fetch_from_ipfs(o.json_cid, as_bytes=False)
                computed = sha256_bytes(canonical_json_bytes(obj)).hex()
                result.computed_json_hash = computed
                result.json_ok = (computed == o.json_hash_onchain)
            except Exception as exc:  # noqa: BLE001
                result.errors.append(f"json verify error: {exc}")

        if verify_image and o.image_cid and o.image_hash_onchain and o.image_hash_onchain != "00" * 32:
            try:
                raw = self.fetch_from_ipfs(o.image_cid, as_bytes=True)
                computed = sha256_bytes(raw).hex()
                result.computed_image_hash = computed
                result.image_ok = (computed == o.image_hash_onchain)
            except Exception as exc:  # noqa: BLE001
                result.errors.append(f"image verify error: {exc}")

        return result
