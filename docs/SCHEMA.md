# Monitor as a Service — Open Schema v1

**Status:** Stable
**Version:** 1.0.0
**License:** CC0 1.0 Universal (public domain)
**Canonical URL:** https://github.com/alejoherrera/stellar_repo/blob/main/docs/SCHEMA.md
**Public viewer:** https://www.obrapublica.info/stellar
**Authors:**
- Master Juan Alejandro Herrera Lopez <alejandroherreracr@gmail.com>
- Andres Herrera Monge, CEO Mivisor <andres.herrera@mivisor.com>
- Claude (Anthropic AI assistant) <noreply@anthropic.com>

This document describes the **public on-chain contract** of the Monitor as a Service
(MaaS) project. Anyone can build dashboards, bots, alerts, mobile apps or analytic
pipelines directly on Stellar + IPFS using only this spec — no permission needed,
no credentials required, no API key from any operator.

If a future hosted convenience API disappears, every consumer can fall back to
reading directly from Stellar Horizon and IPFS gateways using this schema.

---

## 1. Overview

A **Monitor as a Service publisher** is a Stellar account that anchors integrity
metadata of public-infrastructure observations (currently produced by the
[dIAra](https://www.obrapublica.info/ciudadania) AI system, but the schema is
publisher-agnostic). Each observation ("output") consists of:

- A JSON document with structured metadata of a moment in a construction site.
- An associated image captured by an IoT camera.

The schema anchors **hashes and pointers** on Stellar; the actual content lives
on IPFS, content-addressed by CID.

### Pipeline

```
IoT camera -> AI analysis (LLM) -> JSON + image
                                    |
                                    v
                       Pin in IPFS (Pinata or other)
                                    |
                                    v
            Stellar TX with multiple manageData operations
            anchoring SHA-256 hashes + IPFS CIDs + readable metadata
```

### Why this design

- **Verifiable transparency:** any third party can fetch the IPFS content and
  recompute SHA-256 to confirm the on-chain anchor. No trust in the publisher needed.
- **Cheap:** Stellar fees are negligible (~800 stroops per output).
- **Decentralized:** the content is content-addressed; any IPFS node serves the
  same bytes. No single-vendor lock-in for storage.
- **Self-describing:** all metadata needed to interpret an output (project,
  datetime, etc.) is on-chain in human-readable form.

---

## 2. Network and account

A publisher chooses one Stellar network: `testnet` (development, default) or
`public` (mainnet, when production-ready).

- **Horizon endpoints:**
  - testnet: `https://horizon-testnet.stellar.org`
  - mainnet: `https://horizon.stellar.org`
- **Account discovery:** the publisher publishes its public key (G...). To
  fetch all anchored data, query `/accounts/{public_key}`.

A consumer typically only needs:

1. The publisher's public key.
2. The network.
3. This schema document.

---

## 3. Key namespace

All `manageData` keys used by the schema follow these prefixes:

| Prefix | Purpose |
|--------|---------|
| `proj:{code}:` | Project-level metadata (one TX per project, written once). |
| `diara:{output_id}` and `diara:{output_id}:{field}` | Per-output metadata. |
| `maas:` (reserved) | Future schema extensions. |

Implementations MUST NOT write keys outside these prefixes that could collide with
future spec versions. Keys outside the schema namespace are ignored by spec-compliant
consumers but tolerated (forward compatibility).

### 3.1 Project setup keys

Written once when a project starts being monitored. Consumers should expect
exactly these keys per project code:

| Key | UTF-8 value (max 64 bytes) | Required |
|-----|----------------------------|----------|
| `proj:{code}:name` | Human-readable project name | Yes |
| `proj:{code}:partner` | Cooperating institution | Recommended |
| `proj:{code}:url` | Public URL for the project (without `https://`) | Recommended |
| `proj:{code}:system` | Producer system (e.g. `dIAra`) | Recommended |

**Memo of the setup TX:** `dIAra setup v1` (or similar; consumers should not
rely on memo content for parsing).

### 3.2 Output anchor keys

Per output, exactly one Stellar TX with multiple `manageData` operations:

| Key (UTF-8) | Value (binary or UTF-8) | Required |
|-------------|--------------------------|----------|
| `diara:{output_id}` | 64 bytes: `SHA-256(json_canonical) || SHA-256(image)` | Yes |
| `diara:{output_id}:proj` | UTF-8: project code (e.g. `circunvalacion-cr`) | Yes |
| `diara:{output_id}:dt` | UTF-8: original datetime string from JSON (any format) | Recommended |
| `diara:{output_id}:workers` | UTF-8: integer count (string-encoded) | Optional |
| `diara:{output_id}:machinery` | UTF-8: comma-separated list, truncated to 64 bytes | Optional |
| `diara:{output_id}:phase` | UTF-8: construction phase, truncated to 64 bytes | Optional |
| `diara:{output_id}:img_cid` | UTF-8: IPFS CIDv1 base32 of the image | Yes (if image exists) |
| `diara:{output_id}:json_cid` | UTF-8: IPFS CIDv1 base32 of the canonical JSON | Yes |

**Memo of the output TX:** `dIAra ancla v3` (current schema version v1 corresponds
to anchor format v3).

#### Output ID convention

`{output_id}` is RECOMMENDED to be `YYYYMMDD-HHMMSS` matching the original capture
timestamp, but consumers MUST treat it as an opaque string.

#### Hash encoding

The 64-byte value at `diara:{output_id}` is the **binary concatenation** of two
SHA-256 hashes (32 bytes each). Horizon returns this base64-encoded; consumers
must decode base64, then split bytes 0..32 (JSON hash) and 32..64 (image hash).

If no image was available at anchoring time, the image-hash 32 bytes are filled
with zeros (`\x00 * 32`) and `diara:{output_id}:img_cid` is omitted. Consumers
should treat this as "JSON-only anchor".

### 3.3 Reserved field names

Future spec versions may add fields. To avoid collisions, implementations and
extensions MUST NOT use these reserved suffixes after `diara:{output_id}:`:

`hash`, `version`, `signature`, `geo`, `lat`, `lon`, `weather`, `vehicles`,
`workers`, `machinery`, `phase`, `dt`, `proj`, `img_cid`, `json_cid`, `prev`,
`next`, `epoch`, `block`, `tx`, `signer`.

---

## 4. Canonical JSON

The hash anchored under `diara:{output_id}` (first 32 bytes) is the SHA-256 of
the **canonical JSON encoding** of the producer output, defined as:

- UTF-8 encoded.
- Object keys recursively sorted in lexicographic order.
- No whitespace between tokens (separators `","` and `":"`).
- Non-ASCII characters preserved as UTF-8 (no `\uXXXX` escapes for code points >= 0x80).
- No trailing newline.

In Python:

```python
import json, hashlib
canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
sha256 = hashlib.sha256(canonical).hexdigest()
```

In JavaScript:

```javascript
function canonicalJson(value) {
  if (value === null) return "null";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") return JSON.stringify(value);
  if (typeof value === "string") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(canonicalJson).join(",") + "]";
  if (typeof value === "object") {
    const keys = Object.keys(value).sort();
    return "{" + keys.map(k => JSON.stringify(k) + ":" + canonicalJson(value[k])).join(",") + "}";
  }
  throw new Error("Unsupported JSON type");
}
```

Both implementations MUST produce identical bytes for identical inputs.

---

## 5. IPFS conventions

- All CIDs MUST be **CIDv1 base32**.
- Both image and JSON are pinned via any IPFS pinning service (Pinata, Web3.Storage,
  Filebase, self-hosted IPFS node, etc.). The schema is pinning-provider-agnostic.
- A consumer SHOULD try multiple gateways in fallback order to reach the content;
  the bytes are identical regardless of gateway.

### 5.1 Recommended public gateways

```
https://gateway.pinata.cloud/ipfs/
https://ipfs.io/ipfs/
https://dweb.link/ipfs/
https://4everland.io/ipfs/
```

Consumer applications SHOULD implement gateway fallback to handle rate limits
and outages.

---

## 6. Verification procedure

Given an output and access to the publisher's account:

```
1. Fetch publisher account from Horizon: GET /accounts/{public_key}
2. Read account.data, base64-decode each value.
3. Filter keys starting with "diara:{output_id}".
4. Read on-chain hashes from "diara:{output_id}":
   - json_hash_onchain = bytes[0:32]
   - image_hash_onchain = bytes[32:64]
5. Read CIDs from "diara:{output_id}:json_cid" and ":img_cid".
6. Fetch JSON content from any IPFS gateway using json_cid.
7. Compute canonical JSON bytes (see section 4).
8. Compute SHA-256 of those bytes.
9. Verify computed_hash == json_hash_onchain.
10. (Optional) Same for image: fetch raw bytes from img_cid, SHA-256, compare.
```

If both hashes match, the output is **provably authentic**: no party (including
the publisher) can have altered the content after the anchor.

---

## 7. Code examples (minimum viable consumer)

### 7.1 Bash + jq

```bash
ACCOUNT="GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR"
HORIZON="https://horizon-testnet.stellar.org"

# Get all data entries
curl -s "$HORIZON/accounts/$ACCOUNT" | jq '.data'

# Get a specific output's metadata (machinery)
curl -s "$HORIZON/accounts/$ACCOUNT" | \
  jq -r '.data["diara:20251029-060211:machinery"]' | base64 -d
```

### 7.2 Python (no SDK)

```python
import base64, requests, hashlib, json

ACCOUNT = "GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR"
HORIZON = "https://horizon-testnet.stellar.org"

acc = requests.get(f"{HORIZON}/accounts/{ACCOUNT}").json()
data = acc.get("data", {})
outputs = {}
for key, b64val in data.items():
    if not key.startswith("diara:"):
        continue
    parts = key[len("diara:"):].split(":")
    oid = parts[0]
    field = parts[1] if len(parts) > 1 else "_hash"
    raw = base64.b64decode(b64val)
    outputs.setdefault(oid, {})
    outputs[oid][field] = raw

# Verify one output
oid = next(iter(outputs))
o = outputs[oid]
json_cid = o["json_cid"].decode()
content = requests.get(f"https://gateway.pinata.cloud/ipfs/{json_cid}").json()
canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
print("Match:", hashlib.sha256(canonical).digest() == o["_hash"][:32])
```

### 7.3 With the Python SDK

```python
from monitor_as_a_service import Client

client = Client.testnet("GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR")
for output in client.outputs():
    print(output.output_id, output.workers, output.image_url)

# Verify one
result = client.verify("20251029-060211")
print("JSON match:", result.json_ok)
print("Image match:", result.image_ok)
```

---

## 8. Versioning

This document follows semantic versioning:

- **Patch (1.0.x):** clarifications, typos, no behavior change.
- **Minor (1.x.0):** additive changes — new optional fields, new key prefixes,
  backward-compatible.
- **Major (2.0.0):** breaking changes — modified semantics, deprecated keys.

Major version transitions MUST be reflected in the TX memo prefix (e.g. v2 anchors
use memo `dIAra ancla v4` or similar) so consumers can filter by version.

---

## 9. Conformance

A **conforming publisher**:

- Writes only keys defined in this schema.
- Uses canonical JSON encoding for the JSON hash.
- Pins JSON and image to at least one public IPFS provider before submitting the TX.
- Includes the project setup TX before any output anchors of that project.

A **conforming consumer**:

- Falls back across multiple IPFS gateways.
- Verifies SHA-256 hashes against canonical JSON bytes.
- Handles missing optional fields gracefully.
- Tolerates unknown keys outside the schema namespace.

---

## 10. License

This document is dedicated to the public domain via
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).

You may copy, modify, distribute and use this schema for any purpose, commercial
or non-commercial, without permission or attribution. Forks of the schema are
welcome but should be renamed (e.g. `your_org_open_schema_v1`) to avoid confusion.

The reference implementations (Python and JS SDKs, sample apps) are licensed
under MIT separately; see each repository.
