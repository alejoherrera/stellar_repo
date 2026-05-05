"""
04_wow_dashboard.py - Demo end-to-end:
  Stellar testnet -> Decode anchors -> Verify against IPFS -> Interactive dashboard.

Pipeline visible en terminal con rich, dashboard interactivo HTML con plotly.
La data sale 100% de Stellar testnet + IPFS publico. Cero backend, cero API keys.

Install:
    pip install monitor-as-a-service rich plotly

Run:
    python 04_wow_dashboard.py

Output:
    dashboard.html (se abre automaticamente en el navegador)
"""
import time
import webbrowser
from collections import Counter
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from monitor_as_a_service import Client

ACCOUNT = "GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR"

console = Console()


def banner():
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]Monitor as a Service[/]  | live demo\n"
            "[dim]Lee anclas de obra publica desde Stellar testnet,\n"
            "verifica integridad contra IPFS, genera dashboard interactivo.[/]\n"
            "[dim cyan]Schema CC0 |SDK MIT |0 API keys, 0 backend dependencies[/]\n"
            "[bold yellow]Powered by Mivisor.com[/]",
            border_style="cyan",
            padding=(1, 3),
        )
    )


def step(num: int, title: str):
    console.print(f"\n[bold magenta]{num}.[/] [bold]{title}[/]")


def main():
    banner()
    started = time.time()

    # ============================================================
    step(1, "Conectando a Stellar Horizon (testnet)")
    # ============================================================
    client = Client.testnet(ACCOUNT)
    console.print(f"   [dim]Endpoint:[/]  https://horizon-testnet.stellar.org")
    console.print(f"   [dim]Account: [/]  [cyan]{ACCOUNT}[/]")
    console.print(f"   [dim]Explorer:[/]  [link=https://stellar.expert/explorer/testnet/account/{ACCOUNT}]stellar.expert[/]")

    # ============================================================
    step(2, "Leyendo metadata del proyecto on-chain")
    # ============================================================
    proj = client.project()
    if proj:
        meta = Table.grid(padding=(0, 2))
        meta.add_column(style="dim", justify="right")
        meta.add_column(style="bold")
        meta.add_row("Codigo on-chain:", proj.code)
        meta.add_row("Nombre:", proj.name or "(sin nombre)")
        meta.add_row("Sistema productor:", proj.system or "(sin sistema)")
        meta.add_row("Contraparte:", proj.partner or "(sin partner)")
        if proj.url:
            meta.add_row("URL publica:", f"https://{proj.url}")
        console.print(meta)

    # ============================================================
    step(3, "Decodificando data entries on-chain")
    # ============================================================
    outputs = list(client.outputs())
    if not outputs:
        console.print("[red]No hay outputs anclados en esta cuenta.[/]")
        return
    console.print(f"   [green]OK[/] [bold]{len(outputs)}[/] anclas encontradas")
    console.print(f"   [dim]Rango temporal: {outputs[-1].output_id}  ->  {outputs[0].output_id}[/]")
    console.print(f"   [dim]Cada ancla = 8 operaciones manageData (hash + 5 metadatos + 2 CIDs IPFS)[/]")

    # ============================================================
    step(4, "Verificando integridad criptografica (muestra)")
    # ============================================================
    N = min(8, len(outputs))
    sample = outputs[:N]
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            "[cyan]Fetching JSON de IPFS |SHA-256 |comparando con on-chain[/]",
            total=N,
        )
        for o in sample:
            r = client.verify(o.output_id, verify_image=False)
            results.append((o, r))
            progress.advance(task)

    ok = sum(1 for _, r in results if r.json_ok)
    table = Table(title=f"Verificaciones criptograficas ({ok}/{N} OK)", show_lines=False)
    table.add_column("Output ID", style="cyan", no_wrap=True)
    table.add_column("Hash on-chain", style="dim")
    table.add_column("Calculado IPFS", style="dim")
    table.add_column("Match", justify="center")
    for o, r in results:
        match = "[green]OK[/]" if r.json_ok else "[red]X[/]"
        on_chain = (o.json_hash_onchain or "")[:14] + "..."
        computed = (r.computed_json_hash or "")[:14] + "..." if r.computed_json_hash else "—"
        table.add_row(o.output_id, on_chain, computed, match)
    console.print(table)

    # ============================================================
    step(5, "Agregando estadisticas para el dashboard")
    # ============================================================
    phases = Counter(o.phase or "(sin etapa)" for o in outputs)
    machinery = Counter(
        m.strip()
        for o in outputs
        for m in (o.machinery or "").split(",")
        if m.strip() and m.strip().lower() != "ninguna"
    )
    workers_per_output = [(o.datetime or o.output_id, o.workers or 0) for o in sorted(outputs, key=lambda x: x.output_id)]
    total_persona_obs = sum(w for _, w in workers_per_output)

    stats = Table.grid(padding=(0, 2))
    stats.add_column(style="dim", justify="right")
    stats.add_column(style="bold")
    stats.add_row("Etapas constructivas:", str(len(phases)))
    stats.add_row("Tipos de maquinaria:", str(len(machinery)))
    stats.add_row("Persona-observaciones acumuladas:", str(total_persona_obs))
    console.print(stats)

    # ============================================================
    step(6, "Renderizando dashboard HTML interactivo")
    # ============================================================
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        console.print("[yellow]plotly no esta instalado.[/] Skipping dashboard. `pip install plotly` para habilitar.")
        return

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Outputs por etapa constructiva",
            "Maquinaria detectada (top 10)",
            "Personas trabajadoras a lo largo del tiempo",
            "Fuente verificable",
        ),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "table"}]],
        vertical_spacing=0.12,
    )

    fig.add_trace(
        go.Pie(
            labels=list(phases.keys()),
            values=list(phases.values()),
            hole=0.45,
            textinfo="label+percent",
        ),
        row=1, col=1,
    )

    top_m = machinery.most_common(10)
    fig.add_trace(
        go.Bar(
            x=[c for _, c in top_m],
            y=[m for m, _ in top_m],
            orientation="h",
            marker_color="#1a73e8",
        ),
        row=1, col=2,
    )

    fig.add_trace(
        go.Scatter(
            x=[t for t, _ in workers_per_output],
            y=[w for _, w in workers_per_output],
            mode="lines+markers",
            line=dict(color="#fbbf24", width=2),
            marker=dict(size=6),
        ),
        row=2, col=1,
    )

    fig.add_trace(
        go.Table(
            header=dict(
                values=["Atributo", "Valor"],
                fill_color="#0f172a",
                font=dict(color="white", size=12),
                align="left",
            ),
            cells=dict(
                values=[
                    [
                        "Network",
                        "Stellar account",
                        "Outputs anclados",
                        "Esquema",
                        "Verificacion (muestra)",
                        "Costo total fees",
                        "Dependencias backend",
                    ],
                    [
                        "Stellar testnet",
                        f"{ACCOUNT[:8]}...{ACCOUNT[-6:]}",
                        str(len(outputs)),
                        "MaaS Open Schema v1 (CC0)",
                        f"{ok}/{N} OK criptografico",
                        f"~{len(outputs) * 0.00008:.5f} XLM (~$0.00)",
                        "0 (lectura directa Stellar+IPFS)",
                    ],
                ],
                fill_color="#f1f5f9",
                align="left",
                font=dict(size=11),
                height=28,
            ),
        ),
        row=2, col=2,
    )

    fig.update_layout(
        title=dict(
            text=(f"<b>Monitor as a Service</b>  |  {proj.name if proj else ''}"
                  f"<br><span style='font-size:11px; color:#6b7280;'>"
                  f"Powered by <a href='https://mivisor.com' style='color:#1a73e8;'>Mivisor.com</a> "
                  f"&nbsp;|&nbsp; Open Schema CC0 &nbsp;|&nbsp; "
                  f"Stellar testnet (verificable on-chain)</span>"),
            x=0.02,
            y=0.97,
            yanchor="top",
            font=dict(size=20),
        ),
        height=1020,
        showlegend=False,
        margin=dict(t=145, b=80, l=40, r=40),
        plot_bgcolor="white",
        paper_bgcolor="#f8fafc",
    )
    # Empuja los subplot_titles (annotations existentes) ligeramente abajo para no chocar con el title
    fig.update_annotations(yshift=-15)
    # Footer con coautores como annotation adicional paper-anchored
    fig.add_annotation(
        text=("<b>Coautores:</b> Master Juan Alejandro Herrera Lopez &lt;alejandroherreracr@gmail.com&gt; "
              "&nbsp;|&nbsp; Andres Herrera Monge, CEO Mivisor &lt;andres.herrera@mivisor.com&gt; "
              "&nbsp;|&nbsp; Claude (Anthropic AI assistant)"),
        xref="paper", yref="paper",
        x=0.5, y=-0.04,
        xanchor="center", yanchor="top",
        showarrow=False,
        font=dict(size=10, color="#6b7280"),
    )
    fig.update_xaxes(title_text="Datetime", row=2, col=1)
    fig.update_yaxes(title_text="Personas", row=2, col=1)

    out_path = Path("dashboard.html").resolve()
    fig.write_html(
        out_path,
        include_plotlyjs="cdn",
        config={"displayModeBar": False},
    )
    console.print(f"   [green]OK[/] Dashboard escrito en [cyan]{out_path}[/]")

    # ============================================================
    elapsed = time.time() - started
    console.print(
        Panel(
            f"[bold green]Listo en {elapsed:.1f}s[/]\n\n"
            f"[dim]Toda la data viene de Stellar testnet + IPFS publico.\n"
            f"Costo de los {len(outputs)} anclas (mainnet): ~{len(outputs) * 0.00008 * 0.30:.4f} USD a $0.30/XLM.\n"
            f"Costo de tu lectura: 0 (lo hiciste vos en tu maquina).\n"
            f"Dependencias del consumer: 0 backend, 0 API keys, 0 permisos requeridos.[/]",
            border_style="green",
            title="[bold]Transparencia, no demo[/]",
            padding=(1, 3),
        )
    )

    webbrowser.open(f"file://{out_path}")


if __name__ == "__main__":
    main()
