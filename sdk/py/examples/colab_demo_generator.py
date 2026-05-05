"""Genera el notebook colab_demo.ipynb desde Python para evitar problemas de escaping JSON."""
import json
from pathlib import Path


def md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": [l + "\n" for l in lines]}


def code(*lines):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [l + "\n" for l in lines],
    }


cells = [
    md(
        "# Monitor as a Service — Colab Demo",
        "",
        "**Powered by [Mivisor.com](https://mivisor.com)**",
        "",
        "Lee anclas de obra publica desde **Stellar testnet**, verifica integridad contra **IPFS** publico, "
        "y genera un **dashboard interactivo** — todo desde Google Colab, sin servidor propio, sin API keys.",
        "",
        "**Schema CC0** | **SDK MIT** | **0 backend dependencies**",
        "",
        "---",
        "",
        "Coautores: Juan Alejandro Herrera Lopez | Andres Herrera Monge (CEO Mivisor.com) | Claude (Anthropic AI assistant)",
    ),

    md(
        "## 1. Instalar el SDK",
        "",
        "Usamos `--upgrade --force-reinstall` para evitar cache stale en Colab/Jupyter."
    ),
    code("!pip install --quiet --upgrade --force-reinstall monitor-as-a-service ipywidgets plotly pandas"),
    md(
        "**Si es la primera vez que corres esta celda, hace falta reiniciar el runtime** "
        "para que Python pickee la nueva version del paquete:",
        "",
        "1. Menu: `Runtime` → `Restart session` (o `Ctrl+M .`).",
        "2. Volver a correr la celda 2 en adelante (no hace falta reinstalar).",
    ),

    md(
        "## 2. Conectar a Stellar testnet",
        "",
        "El publisher publico de demostracion es la cuenta `GDRWQERI...3JCPFR`. ",
        "Cualquier dev puede consultarla sin permiso. Aqui pedimos su metadata de proyecto."
    ),
    code(
        "from monitor_as_a_service import Client",
        "",
        "ACCOUNT = \"GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR\"",
        "client = Client.testnet(ACCOUNT)",
        "",
        "project = client.project()",
        "print(f\"Proyecto on-chain: {project.name}\")",
        "print(f\"Codigo: {project.code}\")",
        "print(f\"Sistema productor: {project.system}\")",
        "print(f\"Contraparte: {project.partner}\")",
        "print(f\"URL publica: https://{project.url}\")",
    ),

    md(
        "## 3. Listar todos los outputs anclados",
        "",
        "Cada output es una observacion de la obra (foto + JSON con metadata generada por IA), "
        "anclada en una transaccion Stellar con 8 operaciones `manageData` (hash + 5 metadatos legibles + 2 CIDs IPFS)."
    ),
    code(
        "import pandas as pd",
        "",
        "outputs = list(client.outputs())",
        "print(f\"Total outputs anclados: {len(outputs)}\")",
        "print(f\"Rango: {outputs[-1].output_id}  ->  {outputs[0].output_id}\")",
        "print()",
        "",
        "df = pd.DataFrame([{",
        "    \"output_id\": o.output_id,",
        "    \"datetime\": o.datetime,",
        "    \"workers\": o.workers,",
        "    \"machinery\": o.machinery,",
        "    \"phase\": o.phase,",
        "    \"image_url\": o.image_url,",
        "} for o in outputs])",
        "df.head(10)",
    ),

    md(
        "## 4. Ver una imagen anclada",
        "",
        "Las imagenes viven en IPFS — content-addressable, recuperables desde cualquier gateway publico. "
        "Cualquier modificacion en la imagen cambiaria el CID y rompiendo la verificacion."
    ),
    code(
        "from IPython.display import Image, display",
        "",
        "first = outputs[0]",
        "print(f\"Output: {first.output_id}\")",
        "print(f\"Fecha: {first.datetime}\")",
        "print(f\"Phase: {first.phase}\")",
        "print(f\"Image CID: {first.image_cid}\")",
        "print(f\"Hash on-chain (img): {first.image_hash_onchain}\")",
        "print()",
        "display(Image(url=first.image_url, width=600))",
    ),

    md(
        "## 5. Verificar integridad criptografica",
        "",
        "El SDK fetch-ea el JSON desde IPFS, calcula su SHA-256 canonico, y compara con el hash anclado en Stellar. "
        "Si todo cierra, el output es **provadamente autentico** — ni siquiera el publisher puede haberlo alterado retroactivamente."
    ),
    code(
        "result = client.verify(outputs[0].output_id)",
        "print(f\"Output: {result.output_id}\")",
        "print(f\"JSON match: {result.json_ok}\")",
        "print(f\"Image match: {result.image_ok}\")",
        "print(f\"Hash JSON calculado: {result.computed_json_hash}\")",
        "print(f\"Hash JSON on-chain:  {outputs[0].json_hash_onchain}\")",
    ),

    md("Verifiquemos los primeros 5 en lote:"),
    code(
        "for o in outputs[:5]:",
        "    r = client.verify(o.output_id, verify_image=False)",
        "    status = \"OK\" if r.json_ok else \"FAIL\"",
        "    print(f\"  [{status}]  {o.output_id}  -  {(o.phase or '-')[:30]}\")",
    ),

    md(
        "## 6. Dashboard interactivo (plotly)",
        "",
        "Construimos un dashboard inline con los datos leidos. Notese: **toda la data viene de Stellar testnet**, no de un servidor nuestro."
    ),
    code(
        "from collections import Counter",
        "import plotly.graph_objects as go",
        "from plotly.subplots import make_subplots",
        "",
        "phases = Counter(o.phase or \"(sin etapa)\" for o in outputs)",
        "machinery = Counter(",
        "    m.strip() for o in outputs",
        "    for m in (o.machinery or \"\").split(\",\")",
        "    if m.strip() and m.strip().lower() != \"ninguna\"",
        ")",
        "",
        "fig = make_subplots(",
        "    rows=2, cols=2,",
        "    subplot_titles=(",
        "        \"Outputs por etapa constructiva\",",
        "        \"Maquinaria detectada (top 10)\",",
        "        \"Personas trabajadoras a lo largo del tiempo\",",
        "        \"Distribucion de outputs por dia\",",
        "    ),",
        "    specs=[[{\"type\": \"pie\"}, {\"type\": \"bar\"}],",
        "           [{\"type\": \"scatter\"}, {\"type\": \"bar\"}]],",
        "    vertical_spacing=0.16,",
        ")",
        "",
        "fig.add_trace(go.Pie(labels=list(phases), values=list(phases.values()), hole=0.45, textinfo=\"label+percent\"), row=1, col=1)",
        "",
        "top_m = machinery.most_common(10)",
        "fig.add_trace(go.Bar(x=[c for _, c in top_m], y=[m for m, _ in top_m], orientation=\"h\", marker_color=\"#1a73e8\"), row=1, col=2)",
        "",
        "chrono = sorted(outputs, key=lambda x: x.output_id)",
        "fig.add_trace(go.Scatter(x=[o.datetime or o.output_id for o in chrono], y=[o.workers or 0 for o in chrono], mode=\"lines+markers\", line=dict(color=\"#fbbf24\", width=2)), row=2, col=1)",
        "",
        "by_day = Counter(o.output_id[:8] for o in outputs)",
        "days = sorted(by_day)",
        "fig.add_trace(go.Bar(x=days, y=[by_day[d] for d in days], marker_color=\"#10b981\"), row=2, col=2)",
        "",
        "fig.update_layout(",
        "    title=dict(",
        "        text=f\"<b>Monitor as a Service</b> | {project.name}<br>\"",
        "             f\"<span style='font-size:11px; color:#6b7280;'>Powered by Mivisor.com | Schema CC0 | Stellar testnet</span>\",",
        "        x=0.02, y=0.97, yanchor=\"top\", font=dict(size=20),",
        "    ),",
        "    height=900, showlegend=False,",
        "    margin=dict(t=145, b=40, l=40, r=40),",
        "    paper_bgcolor=\"#f8fafc\",",
        ")",
        "fig.update_annotations(yshift=-15)",
        "fig.show()",
    ),

    md(
        "## 7. Bonus: detectar anomalias",
        "",
        "Ahora que tenemos los outputs como DataFrame, encontrar patrones es trivial. ",
        "Por ejemplo: dias con cero personas trabajadoras durante hora laboral (probable suspension de obra)."
    ),
    code(
        "df[\"hour\"] = df[\"output_id\"].str.split(\"-\").str[1].str[:2].astype(int)",
        "labor_hours = df[(df[\"hour\"] >= 7) & (df[\"hour\"] <= 16)]",
        "no_workers = labor_hours[labor_hours[\"workers\"] == 0]",
        "print(f\"Outputs en horario laboral con 0 personas: {len(no_workers)} de {len(labor_hours)}\")",
        "no_workers[[\"output_id\", \"datetime\", \"phase\", \"machinery\"]].head(10)",
    ),

    md(
        "## 8. Widgets interactivos (NUEVO en 1.1.0)",
        "",
        "El SDK incluye widgets de ipywidgets para explorar los datos sin escribir codigo.",
        "",
        "### 8.1 Buscar imagen anclada por fecha y hora",
        "",
        "Calendario + sliders de hora y minuto. El SDK encuentra el output mas cercano y muestra la imagen pineada en IPFS con su metadata."
    ),
    code(
        "from monitor_as_a_service.widgets import image_at_datetime",
        "image_at_datetime(client)",
    ),

    md(
        "### 8.2 Generar dashboard por rango de fechas",
        "",
        "Dos DatePickers + boton. Filtra los outputs en el rango y renderiza un dashboard plotly inline con KPIs y 4 charts."
    ),
    code(
        "from monitor_as_a_service.widgets import dashboard_for_range",
        "dashboard_for_range(client)",
    ),

    md(
        "### 8.3 Helpers programaticos (sin widget)",
        "",
        "Si preferis llamar las funciones directo:"
    ),
    code(
        "# Listar fechas disponibles on-chain",
        "fechas = client.available_dates()",
        "print(f\"{len(fechas)} dias con outputs: {fechas[0]} -> {fechas[-1]}\")",
        "",
        "# Outputs de un dia especifico",
        "octubre_3 = client.outputs_on_date(\"2025-10-03\")",
        "print(f\"3 oct 2025: {len(octubre_3)} outputs\")",
        "",
        "# Outputs de un rango",
        "primera_semana = client.outputs_in_range(\"2025-10-03\", \"2025-10-09\")",
        "print(f\"Primera semana: {len(primera_semana)} outputs\")",
        "",
        "# Output mas cercano a un datetime",
        "cercano = client.find_nearest(\"2025-10-29 14:30:00\")",
        "print(f\"Mas cercano a 14:30 del 29-oct: {cercano.output_id}\")",
    ),

    md(
        "## 8. Que mas se puede construir",
        "",
        "- **Bot Telegram/Discord** que postee cuando entra un output con anomalia",
        "- **Email digest** semanal del estado de la obra",
        "- **Mapa interactivo** con coordenadas (cuando se agreguen al schema)",
        "- **Comparativa entre obras** monitoreadas por distintos publishers",
        "- **Periodismo de datos** con CSV exports",
        "",
        "El schema es CC0. Los SDKs son MIT. Forkea, copia, redistribui — el objetivo es que esto funcione sin nosotros.",
        "",
        "**Recursos:**",
        "- Live dashboard: https://www.obrapublica.info/stellar/dashboard",
        "- Developer hub: https://www.obrapublica.info/stellar/dev",
        "- Schema (CC0): https://github.com/alejoherrera/stellar_repo/blob/main/docs/SCHEMA.md",
        "- Cuenta Stellar testnet: [`GDRWQERI...3JCPFR`](https://stellar.expert/explorer/testnet/account/GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR)",
        "",
        "---",
        "",
        "**Powered by [Mivisor.com](https://mivisor.com)**",
        "",
        "Coautores: Juan Alejandro Herrera Lopez ・ Andres Herrera Monge (CEO Mivisor.com) ・ Claude (Anthropic AI assistant)",
    ),
]

notebook = {
    "cells": cells,
    "metadata": {
        "colab": {
            "provenance": [],
            "toc_visible": True,
        },
        "kernelspec": {
            "display_name": "Python 3",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out = Path(__file__).parent / "colab_demo.ipynb"
out.write_text(json.dumps(notebook, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"OK escrito: {out}")
print(f"Total cells: {len(cells)}")
