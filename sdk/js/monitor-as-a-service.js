/**
 * monitor-as-a-service — Reference JavaScript SDK for the MaaS Open Schema v1.
 *
 * Works in modern browsers (no build) and in Node.js >= 18 (uses global fetch + crypto.subtle).
 * License: MIT.
 *
 * Schema spec: https://github.com/alejoherrera/stellar_repo/blob/main/docs/SCHEMA.md
 *
 * Browser usage:
 *   <script type="module">
 *     import { Client } from "https://www.obrapublica.info/static/monitor-as-a-service.js";
 *     const client = Client.testnet("GDRWQERI...");
 *     for await (const output of client.outputs()) console.log(output);
 *   </script>
 *
 * Node usage:
 *   import { Client } from "monitor-as-a-service";
 *   const client = Client.testnet("GDRWQERI...");
 */

const HORIZONS = {
  testnet: "https://horizon-testnet.stellar.org",
  public: "https://horizon.stellar.org",
};

const DEFAULT_GATEWAYS = [
  "https://gateway.pinata.cloud/ipfs/",
  "https://ipfs.io/ipfs/",
  "https://dweb.link/ipfs/",
  "https://4everland.io/ipfs/",
];

export const VERSION = "1.0.0";
export const SCHEMA_VERSION = "1.0.0";

/** Encode value as canonical JSON per MaaS Open Schema section 4. */
export function canonicalJson(value) {
  if (value === null) return "null";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") {
    if (!isFinite(value)) throw new Error("Non-finite number not supported");
    return JSON.stringify(value);
  }
  if (typeof value === "string") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(canonicalJson).join(",") + "]";
  if (typeof value === "object") {
    const keys = Object.keys(value).sort();
    return "{" + keys.map(k => JSON.stringify(k) + ":" + canonicalJson(value[k])).join(",") + "}";
  }
  throw new Error("Unsupported JSON type");
}

/** SHA-256 helper (Uint8Array or string input -> hex). */
export async function sha256Hex(input) {
  const bytes = typeof input === "string" ? new TextEncoder().encode(input) : input;
  const hash = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

function b64ToBytes(b64) {
  const bin = (typeof atob === "function") ? atob(b64) : Buffer.from(b64, "base64").toString("binary");
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function bytesToHex(bytes) {
  return Array.from(bytes).map(b => b.toString(16).padStart(2, "0")).join("");
}

function bytesToText(bytes) {
  return new TextDecoder("utf-8").decode(bytes);
}

export class Client {
  constructor(account, { horizon = HORIZONS.testnet, gateways = DEFAULT_GATEWAYS } = {}) {
    this.account = account;
    this.horizon = horizon.replace(/\/$/, "");
    this.gateways = gateways;
    this._raw = null;
  }

  static testnet(account, opts = {}) {
    return new Client(account, { ...opts, horizon: HORIZONS.testnet });
  }

  static mainnet(account, opts = {}) {
    return new Client(account, { ...opts, horizon: HORIZONS.public });
  }

  async fetchRaw(force = false) {
    if (this._raw && !force) return this._raw;
    const r = await fetch(`${this.horizon}/accounts/${this.account}`);
    if (!r.ok) throw new Error(`Horizon ${r.status}: ${await r.text()}`);
    this._raw = await r.json();
    return this._raw;
  }

  async project() {
    const data = (await this.fetchRaw()).data || {};
    let code = null;
    const fields = {};
    for (const [k, v] of Object.entries(data)) {
      if (!k.startsWith("proj:")) continue;
      const rest = k.slice("proj:".length);
      const [c, f] = rest.split(":", 2);
      code = c;
      fields[f] = bytesToText(b64ToBytes(v));
    }
    return code ? { code, ...fields } : null;
  }

  async outputs() {
    const data = (await this.fetchRaw()).data || {};
    const agg = {};
    for (const [k, v] of Object.entries(data)) {
      if (!k.startsWith("diara:")) continue;
      const rest = k.slice("diara:".length);
      const parts = rest.split(":");
      const oid = parts[0];
      const field = parts[1] || "_hash";
      const bytes = b64ToBytes(v);
      agg[oid] = agg[oid] || {};
      agg[oid][field] = bytes;
    }
    return Object.keys(agg).sort().reverse().map(oid => {
      const f = agg[oid];
      const hashBlob = f._hash || new Uint8Array(0);
      const jsonHash = hashBlob.length >= 32 ? bytesToHex(hashBlob.slice(0, 32)) : null;
      const imageHash = hashBlob.length >= 64 ? bytesToHex(hashBlob.slice(32, 64)) : null;
      const workers = f.workers ? parseInt(bytesToText(f.workers), 10) : null;
      return {
        outputId: oid,
        projectCode: f.proj ? bytesToText(f.proj) : null,
        datetime: f.dt ? bytesToText(f.dt) : null,
        workers: Number.isFinite(workers) ? workers : null,
        machinery: f.machinery ? bytesToText(f.machinery) : null,
        phase: f.phase ? bytesToText(f.phase) : null,
        jsonCid: f.json_cid ? bytesToText(f.json_cid) : null,
        imageCid: f.img_cid ? bytesToText(f.img_cid) : null,
        jsonHashOnChain: jsonHash,
        imageHashOnChain: imageHash,
        get jsonUrl() { return this.jsonCid ? `https://gateway.pinata.cloud/ipfs/${this.jsonCid}` : null; },
        get imageUrl() { return this.imageCid ? `https://gateway.pinata.cloud/ipfs/${this.imageCid}` : null; },
      };
    });
  }

  async get(outputId) {
    const list = await this.outputs();
    return list.find(o => o.outputId === outputId) || null;
  }

  async fetchFromIPFS(cid, asArrayBuffer = false) {
    let lastErr;
    for (const gw of this.gateways) {
      try {
        const r = await fetch(gw + cid);
        if (!r.ok) { lastErr = new Error(`${gw}: HTTP ${r.status}`); continue; }
        return asArrayBuffer ? new Uint8Array(await r.arrayBuffer()) : await r.json();
      } catch (e) {
        lastErr = e;
      }
    }
    throw lastErr || new Error("All gateways failed");
  }

  async verify(outputId, verifyImage = true) {
    const o = await this.get(outputId);
    if (!o) return { outputId, errors: ["output not found"] };
    const result = { outputId, errors: [] };

    if (!o.jsonCid) {
      result.errors.push("no json_cid anchored");
    } else {
      try {
        const obj = await this.fetchFromIPFS(o.jsonCid, false);
        const computed = await sha256Hex(canonicalJson(obj));
        result.computedJsonHash = computed;
        result.jsonOk = (computed === o.jsonHashOnChain);
      } catch (e) {
        result.errors.push(`json verify error: ${e.message}`);
      }
    }
    if (verifyImage && o.imageCid && o.imageHashOnChain && o.imageHashOnChain !== "00".repeat(32)) {
      try {
        const buf = await this.fetchFromIPFS(o.imageCid, true);
        const computed = await sha256Hex(buf);
        result.computedImageHash = computed;
        result.imageOk = (computed === o.imageHashOnChain);
      } catch (e) {
        result.errors.push(`image verify error: ${e.message}`);
      }
    }
    return result;
  }
}

export default Client;
