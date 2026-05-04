# monitor-as-a-service (JavaScript SDK)

Reference JS SDK for the **MaaS Open Schema v1**. Works in modern browsers (no build) and Node.js >= 18.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

- **Schema:** [`docs/SCHEMA.md`](../../docs/SCHEMA.md) (CC0)
- **Live publisher:** `GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR` (Stellar testnet)
- **Public viewer:** https://www.obrapublica.info/stellar

## Quickstart (browser, no build)

```html
<script type="module">
  import { Client } from "https://www.obrapublica.info/static/monitor-as-a-service.js";
  const client = Client.testnet("GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR");
  const outputs = await client.outputs();
  console.log(outputs.length, "anchors");
  for (const o of outputs.slice(0, 5)) {
    console.log(o.outputId, o.workers, o.phase, o.imageUrl);
  }
</script>
```

## Quickstart (Node.js)

```bash
npm install monitor-as-a-service
```

```js
import { Client } from "monitor-as-a-service";

const client = Client.testnet("GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR");
for (const o of await client.outputs()) console.log(o.outputId, o.workers);

const r = await client.verify("20251029-060211");
console.log("JSON match:", r.jsonOk, "Image match:", r.imageOk);
```

## API

| Method | Description |
|--------|-------------|
| `Client.testnet(account, opts)` / `Client.mainnet(...)` | Build a read-only client. |
| `client.project()` | Returns `{ code, name, partner, url, system }` or `null`. |
| `client.outputs()` | Returns array of outputs (newest first). |
| `client.get(outputId)` | Fetch one output. |
| `client.verify(outputId, verifyImage=true)` | Compute SHA-256 of IPFS content and compare with on-chain. |
| `client.fetchFromIPFS(cid, asArrayBuffer=false)` | Low-level: try gateways with fallback. |

## Examples

- [`examples/01-list-outputs.html`](examples/01-list-outputs.html) — open in browser
- [`examples/02-verify-node.mjs`](examples/02-verify-node.mjs) — run with Node

## License

MIT — see source. Schema is CC0.
