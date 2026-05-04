// Run with: node examples/02-verify-node.mjs (Node 18+)
import { Client } from "../monitor-as-a-service.js";

const ACCOUNT = "GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR";
const OUTPUT_ID = "20251029-060211";

const client = Client.testnet(ACCOUNT);
const o = await client.get(OUTPUT_ID);
console.log("Output:   ", o.outputId);
console.log("Project:  ", o.projectCode);
console.log("Datetime: ", o.datetime);
console.log("Image:    ", o.imageUrl);
console.log("JSON:     ", o.jsonUrl);
console.log();

const result = await client.verify(OUTPUT_ID);
console.log("JSON match:  ", result.jsonOk);
console.log("Image match: ", result.imageOk);
if (result.errors?.length) console.log("Errors:", result.errors);
