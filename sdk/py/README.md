# monitor-as-a-service (Python SDK)

Reference Python implementation of the **MaaS Open Schema v1**.
Reads, parses and verifies dIAra/MaaS anchors directly from Stellar + IPFS — no API key, no centralized backend.

**Powered by [Mivisor.com](https://mivisor.com).**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Coautores

- **Master Juan Alejandro Herrera López** &lt;alejandroherreracr@gmail.com&gt; — autor principal
- **Andrés Herrera Monge**, CEO [Mivisor.com](https://mivisor.com) &lt;andres.herrera@mivisor.com&gt; — coautor
- **Claude** (Anthropic AI assistant) &lt;noreply@anthropic.com&gt; — coautor de implementación (código, schema, SDKs)

- **Schema:** [`docs/SCHEMA.md`](../../docs/SCHEMA.md) (CC0)
- **Live publisher:** `GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR` (Stellar testnet)
- **Public viewer:** https://www.obrapublica.info/stellar

## Install

From source (until published to PyPI):

```bash
pip install -e ./sdk/py
# or, if using requirements.txt: -e git+https://github.com/alejoherrera/stellar_repo.git#subdirectory=sdk/py&egg=monitor_as_a_service
```

## Quickstart

```python
from monitor_as_a_service import Client

client = Client.testnet("GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR")

project = client.project()
print(project.name, project.partner)

for o in client.outputs():
    print(o.output_id, o.workers, o.phase, o.image_url)

# Verify cryptographic integrity of one output
result = client.verify("20251029-060211")
print("JSON match:", result.json_ok, "Image match:", result.image_ok)
```

## API

### `Client.testnet(account)` / `Client.mainnet(account)`
Builds a read-only client. Optional kwargs: `gateways=[...]`, `timeout=30`.

### `client.project() -> Project | None`
Returns the project metadata (name, partner, url, system) read from `proj:{code}:*` keys.

### `client.outputs() -> Iterator[Output]`
Iterates over all anchored outputs, newest first.

### `client.get(output_id) -> Output | None`
Fetches a specific output.

### `client.verify(output_id, verify_image=True) -> VerificationResult`
Fetches content from IPFS gateways (with fallback) and compares SHA-256 against on-chain anchors.

### `client.fetch_from_ipfs(cid, as_bytes=False)`
Low-level: try each gateway, return parsed JSON or raw bytes.

## Examples

- [`examples/01_list_outputs.py`](examples/01_list_outputs.py) — table of all outputs
- [`examples/02_verify_one.py`](examples/02_verify_one.py) — verify one output end-to-end
- [`examples/03_export_csv.py`](examples/03_export_csv.py) — dump everything to CSV

## License

MIT — see source. The schema itself is CC0.
