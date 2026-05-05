"""monitor_as_a_service — Reference Python SDK for the MaaS Open Schema v1.

Reads, parses and verifies dIAra/MaaS anchors from Stellar testnet/mainnet
and IPFS public gateways. License: MIT.

Quick start:
    from monitor_as_a_service import Client
    client = Client.testnet("GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR")
    for output in client.outputs():
        print(output.output_id, output.workers, output.machinery)

Schema spec: https://github.com/alejoherrera/stellar_repo/blob/main/docs/SCHEMA.md
"""
from .client import Client, Output, Project, VerificationResult

__version__ = "1.0.2"
__schema_version__ = "1.0.0"
__powered_by__ = "Mivisor.com"
__all__ = ["Client", "Output", "Project", "VerificationResult"]
