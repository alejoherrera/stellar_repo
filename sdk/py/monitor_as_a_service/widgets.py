"""Widgets interactivos para Jupyter / Google Colab.

Uso:
    from monitor_as_a_service import Client
    from monitor_as_a_service.widgets import image_at_datetime, dashboard_for_range

    client = Client.testnet("GDRWQERI...")
    image_at_datetime(client)       # date+time picker -> imagen anclada mas cercana
    dashboard_for_range(client)     # date range picker -> dashboard plotly

Dependencias opcionales (lazy import):
    pip install ipywidgets plotly

Powered by Mivisor.com.
"""
from __future__ import annotations

from collections import Counter
from datetime import date as _date

from .client import Client


def _ensure_deps():
    try:
        import ipywidgets  # noqa: F401
    except ImportError as exc:
        raise ImportError("Falta ipywidgets. Instalar con: pip install ipywidgets") from exc
    try:
        import plotly  # noqa: F401
    except ImportError as exc:
        raise ImportError("Falta plotly. Instalar con: pip install plotly") from exc


def image_at_datetime(client: Client):
    """Renderiza un widget en la celda actual del notebook con:
    - DatePicker, sliders de hora y minuto.
    - Boton 'Buscar imagen' que trae el output anclado mas cercano y lo muestra inline.
    """
    _ensure_deps()
    import ipywidgets as ipw
    from IPython.display import display, Image, HTML, clear_output

    available = client.available_dates()
    if not available:
        display(HTML("<p>No hay outputs anclados en esta cuenta.</p>"))
        return

    min_d = _date.fromisoformat(available[0])
    max_d = _date.fromisoformat(available[-1])

    title = ipw.HTML(
        "<h3 style='margin:0 0 .25rem'>Buscar imagen anclada por fecha y hora</h3>"
        f"<p style='margin:0 0 .75rem; color:#6b7280;'>Rango disponible on-chain: <code>{available[0]}</code> a <code>{available[-1]}</code></p>"
    )
    date_pick = ipw.DatePicker(description="Fecha:", value=max_d)
    hour = ipw.IntSlider(value=12, min=0, max=23, description="Hora:", continuous_update=False)
    minute = ipw.IntSlider(value=0, min=0, max=59, step=5, description="Minuto:", continuous_update=False)
    btn = ipw.Button(description="Buscar imagen mas cercana", button_style="primary", icon="search")
    out = ipw.Output()

    def on_click(_):
        with out:
            clear_output()
            d = date_pick.value
            if not d:
                print("Seleccionar una fecha primero.")
                return
            target = f"{d.strftime('%Y%m%d')}-{hour.value:02d}{minute.value:02d}00"
            o = client.find_nearest(target)
            if not o:
                print("No se encontro output cercano.")
                return
            display(HTML(
                f"<div style='font-family:system-ui;'>"
                f"<h4 style='margin:.5rem 0;'>Output anclado mas cercano: <code>{o.output_id}</code></h4>"
                f"<p style='margin:.25rem 0; color:#374151;'>"
                f"<b>Fecha registrada:</b> {o.datetime or '-'}<br>"
                f"<b>Personas trabajadoras:</b> {o.workers if o.workers is not None else '-'}<br>"
                f"<b>Maquinaria:</b> {o.machinery or '-'}<br>"
                f"<b>Etapa constructiva:</b> {o.phase or '-'}<br>"
                f"<b>Hash JSON on-chain:</b> <code style='font-size:.8em;'>{o.json_hash_onchain}</code><br>"
                f"<b>Image CID (IPFS):</b> <a href='{o.image_url}' target='_blank' style='font-size:.8em;'>{o.image_cid}</a>"
                f"</p></div>"
            ))
            if o.image_url:
                display(Image(url=o.image_url, width=720))
            display(HTML("<p style='font-size:.8em; color:#6b7280; margin-top:.5rem;'>Powered by Mivisor.com | Stellar testnet</p>"))

    btn.on_click(on_click)
    display(ipw.VBox([title, ipw.HBox([date_pick, hour, minute]), btn, out]))


def dashboard_for_range(client: Client):
    """Renderiza un widget con dos DatePickers (desde/hasta) y un boton 'Generar dashboard'.
    Al hacer click filtra los outputs en el rango y genera un dashboard plotly inline."""
    _ensure_deps()
    import ipywidgets as ipw
    import plotly.graph_objects as go
    import plotly.io as pio
    from plotly.subplots import make_subplots
    from IPython.display import display, HTML, clear_output

    # En Colab/Jupyter dentro de un ipywidgets.Output, fig.show() no renderiza.
    # Usamos display(fig) que invoca _repr_html_ y muestra el chart inline.
    # Tambien forzamos el renderer "notebook" como fallback global.
    try:
        if pio.renderers.default in (None, "browser"):
            pio.renderers.default = "notebook"
    except Exception:
        pass

    available = client.available_dates()
    if not available:
        display(HTML("<p>No hay outputs anclados en esta cuenta.</p>"))
        return

    min_d = _date.fromisoformat(available[0])
    max_d = _date.fromisoformat(available[-1])

    title = ipw.HTML(
        "<h3 style='margin:0 0 .25rem'>Dashboard interactivo por rango de fechas</h3>"
        f"<p style='margin:0 0 .75rem; color:#6b7280;'>Datos disponibles on-chain: <code>{available[0]}</code> a <code>{available[-1]}</code> ({len(available)} dias)</p>"
    )
    start_pick = ipw.DatePicker(description="Desde:", value=min_d)
    end_pick = ipw.DatePicker(description="Hasta:", value=max_d)
    btn = ipw.Button(description="Generar dashboard", button_style="primary", icon="chart-bar")
    out = ipw.Output()

    def on_click(_):
        with out:
            clear_output()
            if not start_pick.value or not end_pick.value:
                print("Seleccionar ambas fechas.")
                return
            outs = client.outputs_in_range(start_pick.value, end_pick.value)
            if not outs:
                display(HTML(f"<p>No hay outputs entre <code>{start_pick.value}</code> y <code>{end_pick.value}</code>.</p>"))
                return

            phases = Counter(o.phase or "(sin etapa)" for o in outs)
            machinery = Counter(
                m.strip() for o in outs
                for m in (o.machinery or "").split(",")
                if m.strip() and m.strip().lower() != "ninguna"
            )
            chrono = sorted(outs, key=lambda x: x.output_id)
            by_day = Counter(o.output_id[:8] for o in outs)
            days = sorted(by_day)
            persona_obs = sum(o.workers or 0 for o in outs)

            display(HTML(
                f"<div style='display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:.75rem;'>"
                f"<div style='background:#f1f5f9; padding:.5rem 1rem; border-radius:6px;'><b>{len(outs)}</b> outputs</div>"
                f"<div style='background:#f1f5f9; padding:.5rem 1rem; border-radius:6px;'><b>{len(phases)}</b> etapas</div>"
                f"<div style='background:#f1f5f9; padding:.5rem 1rem; border-radius:6px;'><b>{len(machinery)}</b> tipos maquinaria</div>"
                f"<div style='background:#f1f5f9; padding:.5rem 1rem; border-radius:6px;'><b>{persona_obs}</b> persona-observaciones</div>"
                f"</div>"
            ))

            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    "Outputs por etapa constructiva",
                    "Maquinaria detectada (top 10)",
                    "Personas trabajadoras a lo largo del tiempo",
                    "Outputs por dia",
                ),
                specs=[[{"type": "pie"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "bar"}]],
                vertical_spacing=0.16,
            )
            fig.add_trace(go.Pie(labels=list(phases), values=list(phases.values()), hole=0.45, textinfo="label+percent"), row=1, col=1)
            top_m = machinery.most_common(10)
            fig.add_trace(go.Bar(x=[c for _, c in top_m], y=[m for m, _ in top_m], orientation="h", marker_color="#1a73e8"), row=1, col=2)
            fig.add_trace(go.Scatter(x=[o.datetime or o.output_id for o in chrono], y=[o.workers or 0 for o in chrono], mode="lines+markers", line=dict(color="#fbbf24", width=2)), row=2, col=1)
            fig.add_trace(go.Bar(x=days, y=[by_day[d] for d in days], marker_color="#10b981"), row=2, col=2)
            fig.update_layout(
                title=dict(
                    text=(f"<b>Dashboard {start_pick.value} a {end_pick.value}</b>"
                          f"<br><span style='font-size:11px; color:#6b7280;'>"
                          f"{len(outs)} outputs anclados en Stellar testnet | Powered by Mivisor.com</span>"),
                    x=0.02, y=0.97, yanchor="top", font=dict(size=18),
                ),
                height=820, showlegend=False,
                margin=dict(t=120, b=40, l=40, r=40),
                plot_bgcolor="white", paper_bgcolor="#f8fafc",
            )
            fig.update_annotations(yshift=-12)
            # display(fig) en lugar de fig.show() para que renderice dentro de ipw.Output en Colab
            display(fig)

    btn.on_click(on_click)
    display(ipw.VBox([title, ipw.HBox([start_pick, end_pick]), btn, out]))
