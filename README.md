# stellar_repo — Monitor as a Service

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alejoherrera/stellar_repo/blob/main/sdk/py/examples/colab_demo.ipynb)
[![PyPI](https://img.shields.io/pypi/v/monitor-as-a-service?label=PyPI)](https://pypi.org/project/monitor-as-a-service/)
[![npm](https://img.shields.io/npm/v/monitor-as-a-service?label=npm)](https://www.npmjs.com/package/monitor-as-a-service)
[![License: MIT](https://img.shields.io/badge/SDKs-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Schema: CC0](https://img.shields.io/badge/Schema-CC0-green.svg)](docs/SCHEMA.md)

Documentación conceptual y de arquitectura para el uso de **Stellar** y **Soroban** como infraestructura de transparencia, monitoreo y financiamiento de **obra pública en LATAM**, integrando IA, validación ciudadana y banca de desarrollo.

**Powered by [Mivisor.com](https://mivisor.com).** Live: [obrapublica.info/stellar](https://www.obrapublica.info/stellar) | [/dashboard](https://www.obrapublica.info/stellar/dashboard) | [/dev](https://www.obrapublica.info/stellar/dev) | [/timelapse](https://www.obrapublica.info/stellar/timelapse)

## Try it now (no install)

**Python (Colab notebook):**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alejoherrera/stellar_repo/blob/main/sdk/py/examples/colab_demo.ipynb)

Click el badge — abre el notebook en Google Colab, conecta a Stellar testnet, lista 100+ outputs anclados, verifica integridad criptográfica contra IPFS, genera dashboard interactivo. Cero credenciales, cero install.

**JavaScript (demos en navegador):**

- [Live verification demo](https://cdn.jsdelivr.net/gh/alejoherrera/stellar_repo@main/sdk/js/examples/03-live-verify.html) — verifica un output: descarga JSON+imagen desde IPFS, recomputa SHA-256 contra el hash on-chain. Source: [`sdk/js/examples/03-live-verify.html`](sdk/js/examples/03-live-verify.html).
- [Live dashboard interactivo](https://cdn.jsdelivr.net/gh/alejoherrera/stellar_repo@main/sdk/js/examples/04-dashboard.html) — pipeline visible (6 pasos), metadata del proyecto, 100+ outputs decodificados, verificacion criptografica de muestra y dashboard Plotly con etapas / maquinaria / personas-en-el-tiempo. Mismas vistas que el notebook Python. Source: [`sdk/js/examples/04-dashboard.html`](sdk/js/examples/04-dashboard.html).

Ambos paginas son HTML self-contained que cargan el SDK desde jsDelivr — sin build, sin install. Tambien podes descargarlas y abrirlas local con doble-click.

## Estado

**Fase 1 operativa en testnet.** La evidencia de obra se ancla en Stellar testnet con datos reales (100+ outputs anclados), las imágenes y JSON viven en IPFS (verificables por SHA-256), y los SDKs están publicados en **PyPI** y **npm** con un viewer público en vivo. El gemelo de transparencia con Soroban (Fase 2) y el bono tokenizado (Fase 3) son la aspiración del roadmap, aún no construidos. Ver `docs/specs/`.

## Metodología — Spec-Driven Development (SDD)

Este proyecto se construye con **SDD (R36):** `CONSTITUTION.md` → spec (`docs/specs/`) → contrato → código. Ninguna funcionalidad llega a código sin una spec aprobada que acredite cumplimiento constitucional. Specs vigentes: **Fase 1** (anclaje en Stellar, implementada en testnet) y **Fase 2** (gemelo de transparencia con Soroban). El [Open Anchor Schema (CC0)](docs/SCHEMA.md) es el contrato público on-chain.

## Idea en una línea

Una arquitectura por **fases** que parte del **anclaje en Stellar de la evidencia de obra producida por un sistema de monitoreo con IA + IoT** (sistema externo, fuente de insumos), evoluciona hacia un **gemelo on-chain de transparencia** que además registra eventos de pago de SICOP/Hacienda y emite alertas públicas via smart contracts Soroban, y culmina en un **bono tokenizado emitido por un banco de desarrollo** para financiar obra pública con auditabilidad continua. Existe un fallback (escrow piloto) si Fase 3 no se asegura partner bancario en plazo razonable.

## Alcance

- Caso de uso: obra pública en Costa Rica (gobierno central, municipalidades, infraestructura financiada por banca de desarrollo).
- Audiencia técnica: ingenieria de blockchain (Stellar/Soroban) y backend (Python/JS).
- Audiencia institucional: CGR, BCIE, SUGEVAL, SUGEF, BCCR, Banco Popular, IFAM, MOPT, municipalidades, cooperación internacional (BID, Banco Mundial).

## Índice de documentos

### Disponibles

1. [Motivacion y contexto](docs/01_motivacion_y_contexto.md) — el problema que se busca resolver y por que Stellar.
2. [Casos de uso](docs/02_casos_de_uso.md) — desde notarizacion pasiva hasta bono tokenizado.
3. [Roadmap por fases](docs/09_roadmap_etapas.md) — Fase 0 (monitoreo IA+IoT externo) → Fase 1 (anclaje en Stellar) → Fase 2 (gemelo de transparencia + alertas) → Fase 3 (bono tokenizado), con fallback Fase 2.5 (escrow piloto).
4. [Open Anchor Schema v1 (CC0)](docs/SCHEMA.md) — contrato público on-chain para que terceros construyan sobre los datos sin permiso.

### Specs (R36 spec-driven development)

- [Fase 1 — Anclaje en Stellar de outputs del sistema de monitoreo](docs/specs/2026-05-02_fase1_anclaje_stellar.md) — schema v3 implementado en testnet.
- [Fase 2 — Gemelo de transparencia con alertas Soroban](docs/specs/2026-05-02_fase2_gemelo_transparencia.md) — pre-requisito: Fase 1 en mainnet.

### Pendientes (a redactar según avance del roadmap)

- Arquitectura propuesta detallada
- Comparativa de blockchains (Stellar vs Hedera HCS vs Polygon/EAS vs Algorand vs Arweave)
- Validación ciudadana — cuatro capas y limitaciones
- Tokenizacion y banco de desarrollo — variantes de instrumento y precedentes
- Interoperabilidad bancaria — SEPs, anchors, gap costarricense
- Marco regulatorio CR — SUGEVAL, SUGEF, Ley 7732, Ley 7428
- Spec Fase 3 (bloqueada por dependencias no-técnicas: partner bancario, regulatorio)
- Dudas pendientes — preguntas R40 sin responder

## SDKs

- [`sdk/py/`](sdk/py/) — Python SDK (MIT). Publicado en PyPI: `pip install monitor-as-a-service`.
- [`sdk/js/`](sdk/js/) — JavaScript SDK (MIT). Publicado en npm: `npm install monitor-as-a-service`. Tambien importable directo desde [jsDelivr CDN](https://cdn.jsdelivr.net/npm/monitor-as-a-service) sin build:
  ```html
  <script type="module">
    import { Client } from "https://cdn.jsdelivr.net/npm/monitor-as-a-service@latest/monitor-as-a-service.js";
    const client = Client.testnet("GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR");
    console.log(await client.outputs());
  </script>
  ```

## Sample apps

- [`viewer/`](viewer/) — viewer principal en `/stellar`.
- [`viewer/deploy/stellar_timelapse.html`](viewer/deploy/stellar_timelapse.html) — timelapse animado en `/stellar/timelapse`.
- Dev hub: https://www.obrapublica.info/stellar/dev

## Specs

Specs vigentes (modelo de fases vigente desde Constitution v0.2):

- [Fase 1 — Anclaje en Stellar de outputs del sistema de monitoreo](docs/specs/2026-05-02_fase1_anclaje_stellar.md) — primer paso construible. Imagenes raw en IPFS, transacciones nativas Stellar (sin Soroban). Borrador para revision.
- [Fase 2 — Gemelo de transparencia con alertas Soroban](docs/specs/2026-05-02_fase2_gemelo_transparencia.md) — registro de pagos SICOP/Hacienda + smart contracts consultivos que emiten alertas. Borrador para revision. Pre-requisito: Fase 1 desplegada en mainnet.
- Fase 3 — Bono tokenizado piloto: spec pendiente de redactar (bloqueada por dependencias no-técnicas, ver `docs/09_roadmap_etapas.md`).

Spec historica del modelo previo (3 etapas con escrow): no se redactó archivo final; el modelo fue reemplazado en CONSTITUTION v0.2 antes de llegar a código.

## Divulgación

Material derivado de este repositorio presentado en:

- **TicoBlockchain 2026 — Blockchain & Fintech Day** · 14 de mayo, Hotel Barceló San José. Ponencia: *"Generación de una red de monitoreo de obra pública mediante IoT, modelos de IA y blockchain"*.

## Constitución

Ver [`CONSTITUTION.md`](CONSTITUTION.md). Cualquier spec o decisión técnica debe acreditar cumplimiento constitucional antes de avanzar a código.

## Repos relacionados

- **`ponencia`** (privado, GitHub): https://github.com/alejoherrera/ponencia — repositorio **teorico** con el material para la ponencia CIGEPRO 2026 ("Fortaleciendo la gobernanza de la ejecución de obra pública con tecnologías 4.0 viables en la region: IA, IoT y blockchain para el monitoreo en tiempo real"), el paper original 2021 OLACEFS y el Informe del Grupo Asesor de Expertos en anticorrupcion para LAC.
- **`stellar_repo`** (este repo, local): repositorio de **código** — contratos Soroban, servicios off-chain y specs ejecutables que materializan las ideas planteadas en la ponencia.

La ponencia describe el "que" y el "por que"; este repo describe el "como" y construye el sistema.

## Convenciones

- **Spec-driven (R36):** Constitution -> Spec -> Contract -> Plan -> Tasks -> Code. Sin excepciones.
- **Sin secretos en código (R1):** llaves Stellar y credenciales solo en Google Secret Manager.
- **Encoding (R5):** sin emojis en archivos ni en logs (consola Windows usa codepage 1252).
- **Idioma:** documentación en español; comentarios de código y nombres de contratos en ingles cuando aplique para legibilidad internacional.

## Licencia

Pendiente de definir. Por defecto: todos los derechos reservados hasta que se defina si se libera bajo MIT, Apache-2.0 o licencia restringida (en caso de adopcion institucional).

## Autores

-  Juan Alejandro Herrera Lopez — alejandroherreracr@gmail.com
- Andres Herrera Monge, CEO Mivisor — andres.herrera@mivisor.com
- Claude (Anthropic AI assistant) — co-autor de implementación (código, schema, SDKs)
