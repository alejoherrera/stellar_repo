"""Verify integridad de un output: fetch desde IPFS, compara SHA-256 con on-chain."""
from monitor_as_a_service import Client

ACCOUNT = "GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR"
OUTPUT_ID = "20251029-060211"

client = Client.testnet(ACCOUNT)
o = client.get(OUTPUT_ID)
if not o:
    raise SystemExit(f"Output {OUTPUT_ID} not found on chain")

print(f"Output:   {o.output_id}")
print(f"Project:  {o.project_code}")
print(f"Datetime: {o.datetime}")
print(f"Image:    {o.image_url}")
print(f"JSON:     {o.json_url}")
print()

result = client.verify(OUTPUT_ID)
print(f"JSON match:  {result.json_ok}")
print(f"Image match: {result.image_ok}")
if result.errors:
    print(f"Errors: {result.errors}")
