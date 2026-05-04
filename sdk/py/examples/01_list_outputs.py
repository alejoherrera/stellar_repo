"""List all anchored outputs of a MaaS publisher."""
from monitor_as_a_service import Client

ACCOUNT = "GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR"

client = Client.testnet(ACCOUNT)
project = client.project()
print(f"Proyecto: {project.name} ({project.code})  Partner: {project.partner}")
print(f"URL publica: https://{project.url}")
print()
print(f"{'Output ID':<22}  {'Workers':<8}  {'Phase':<28}  {'Machinery'}")
print("-" * 100)
for o in client.outputs():
    print(f"{o.output_id:<22}  {str(o.workers or '-'):<8}  {(o.phase or '-')[:28]:<28}  {(o.machinery or '-')[:40]}")
