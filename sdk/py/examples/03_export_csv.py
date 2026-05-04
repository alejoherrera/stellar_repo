"""Exporta todos los outputs a CSV (util para journalists / OSINT analysts)."""
import csv
import sys

from monitor_as_a_service import Client

ACCOUNT = "GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR"

client = Client.testnet(ACCOUNT)
writer = csv.writer(sys.stdout)
writer.writerow([
    "output_id", "project", "datetime", "workers", "machinery", "phase",
    "json_cid", "image_cid", "json_hash_onchain", "image_hash_onchain",
])
for o in client.outputs():
    writer.writerow([
        o.output_id, o.project_code, o.datetime, o.workers, o.machinery, o.phase,
        o.json_cid, o.image_cid, o.json_hash_onchain, o.image_hash_onchain,
    ])
