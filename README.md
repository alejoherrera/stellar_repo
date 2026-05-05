# stellar_repo — Monitor as a Service

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alejoherrera/stellar_repo/blob/main/sdk/py/examples/colab_demo.ipynb)
[![PyPI](https://img.shields.io/pypi/v/monitor-as-a-service?label=PyPI)](https://pypi.org/project/monitor-as-a-service/)
[![License: MIT](https://img.shields.io/badge/SDKs-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Schema: CC0](https://img.shields.io/badge/Schema-CC0-green.svg)](docs/SCHEMA.md)

Documentacion conceptual y de arquitectura para el uso de **Stellar** y **Soroban** como infraestructura de transparencia, monitoreo y financiamiento de **obra publica en Costa Rica**, integrando IA, validacion ciudadana y banca de desarrollo.

**Powered by [Mivisor.com](https://mivisor.com).** Live: [obrapublica.info/stellar](https://www.obrapublica.info/stellar) | [/dashboard](https://www.obrapublica.info/stellar/dashboard) | [/dev](https://www.obrapublica.info/stellar/dev) | [/timelapse](https://www.obrapublica.info/stellar/timelapse)

## Try it now (no install)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alejoherrera/stellar_repo/blob/main/sdk/py/examples/colab_demo.ipynb)

Click el badge — abre el notebook en Google Colab, conecta a Stellar testnet, lista 100+ outputs anclados, verifica integridad criptografica contra IPFS, genera dashboard interactivo. Cero credenciales, cero install.

## Estado

**Pre-codigo / fase de exploracion conceptual.** Este repo recoge el resultado de una sesion de exploracion del 2026-04-29 / 2026-04-30. Aun no contiene contratos Soroban ni servicios desplegados. Es la base sobre la que se levantaran specs ejecutables (ver `docs/specs/`).

## Idea en una linea

Una arquitectura por **fases** que parte del **anclaje en Stellar de la evidencia de obra producida por dIAra** (sistema externo de IA + IoT, fuente de insumos), evoluciona hacia un **gemelo on-chain de transparencia** que ademas registra eventos de pago de SICOP/Hacienda y emite alertas publicas via smart contracts Soroban, y culmina en un **bono tokenizado emitido por un banco de desarrollo** para financiar obra publica con auditabilidad continua. Existe un fallback (escrow piloto) si Fase 3 no se asegura partner bancario en plazo razonable.

## Alcance

- Caso de uso: obra publica en Costa Rica (gobierno central, municipalidades, infraestructura financiada por banca de desarrollo).
- Audiencia tecnica: ingenieria de blockchain (Stellar/Soroban) y backend (Python/JS).
- Audiencia institucional: CGR, BCIE, SUGEVAL, SUGEF, BCCR, Banco Popular, IFAM, MOPT, municipalidades, cooperacion internacional (BID, Banco Mundial).

## Indice de documentos

### Disponibles

1. [Motivacion y contexto](docs/01_motivacion_y_contexto.md) — el problema que se busca resolver y por que Stellar.
2. [Casos de uso](docs/02_casos_de_uso.md) — desde notarizacion pasiva hasta bono tokenizado.
3. [Roadmap por fases](docs/09_roadmap_etapas.md) — Fase 0 (dIAra externa) → Fase 1 (anclaje en Stellar) → Fase 2 (gemelo de transparencia + alertas) → Fase 3 (bono tokenizado), con fallback Fase 2.5 (escrow piloto).
4. [Open Anchor Schema v1 (CC0)](docs/SCHEMA.md) — contrato publico on-chain para que terceros construyan sobre los datos sin permiso.

### Specs (R36 spec-driven development)

- [Fase 1 — Anclaje en Stellar de outputs de dIAra](docs/specs/2026-05-02_fase1_anclaje_stellar.md) — schema v3 implementado en testnet.
- [Fase 2 — Gemelo de transparencia con alertas Soroban](docs/specs/2026-05-02_fase2_gemelo_transparencia.md) — pre-requisito: Fase 1 en mainnet.

### Pendientes (a redactar segun avance del roadmap)

- Arquitectura propuesta detallada
- Comparativa de blockchains (Stellar vs Hedera HCS vs Polygon/EAS vs Algorand vs Arweave)
- Validacion ciudadana — cuatro capas y limitaciones
- Tokenizacion y banco de desarrollo — variantes de instrumento y precedentes
- Interoperabilidad bancaria — SEPs, anchors, gap costarricense
- Marco regulatorio CR — SUGEVAL, SUGEF, Ley 7732, Ley 7428
- Spec Fase 3 (bloqueada por dependencias no-tecnicas: partner bancario, regulatorio)
- Dudas pendientes — preguntas R40 sin responder

## SDKs

- [`sdk/py/`](sdk/py/) — Python SDK (MIT). `pip install -e ./sdk/py` o desde GitHub.
- [`sdk/js/`](sdk/js/) — JavaScript SDK (MIT). Importable directo en navegador via `https://www.obrapublica.info/static/monitor-as-a-service.js` o como ES module en Node 18+.

## Sample apps

- [`viewer/`](viewer/) — viewer principal en `/stellar`.
- [`viewer/deploy/stellar_timelapse.html`](viewer/deploy/stellar_timelapse.html) — timelapse animado en `/stellar/timelapse`.
- Dev hub: https://www.obrapublica.info/stellar/dev

## Specs

Specs vigentes (modelo de fases vigente desde Constitution v0.2):

- [Fase 1 — Anclaje en Stellar de outputs de dIAra](docs/specs/2026-05-02_fase1_anclaje_stellar.md) — primer paso construible. Imagenes raw en IPFS, transacciones nativas Stellar (sin Soroban). Borrador para revision.
- [Fase 2 — Gemelo de transparencia con alertas Soroban](docs/specs/2026-05-02_fase2_gemelo_transparencia.md) — registro de pagos SICOP/Hacienda + smart contracts consultivos que emiten alertas. Borrador para revision. Pre-requisito: Fase 1 desplegada en mainnet.
- Fase 3 — Bono tokenizado piloto: spec pendiente de redactar (bloqueada por dependencias no-tecnicas, ver `docs/09_roadmap_etapas.md`).

Spec historica del modelo previo (3 etapas con escrow): no se redactó archivo final; el modelo fue reemplazado en CONSTITUTION v0.2 antes de llegar a codigo.

## Constitucion

Ver [`CONSTITUTION.md`](CONSTITUTION.md). Cualquier spec o decision tecnica debe acreditar cumplimiento constitucional antes de avanzar a codigo.

## Repos relacionados

- **`ponencia`** (privado, GitHub): https://github.com/alejoherrera/ponencia — repositorio **teorico** con el material para la ponencia CIGEPRO 2026 ("Fortaleciendo la gobernanza de la ejecucion de obra publica con tecnologias 4.0 viables en la region: IA, IoT y blockchain para el monitoreo en tiempo real"), el paper original 2021 OLACEFS y el Informe del Grupo Asesor de Expertos en anticorrupcion para LAC.
- **`stellar_repo`** (este repo, local): repositorio de **codigo** — contratos Soroban, servicios off-chain y specs ejecutables que materializan las ideas planteadas en la ponencia.

La ponencia describe el "que" y el "por que"; este repo describe el "como" y construye el sistema.

## Convenciones

- **Spec-driven (R36):** Constitution -> Spec -> Contract -> Plan -> Tasks -> Code. Sin excepciones.
- **Sin secretos en codigo (R1):** llaves Stellar y credenciales solo en Google Secret Manager.
- **Encoding (R5):** sin emojis en archivos ni en logs (consola Windows usa codepage 1252).
- **Idioma:** documentacion en espanol; comentarios de codigo y nombres de contratos en ingles cuando aplique para legibilidad internacional.

## Licencia

Pendiente de definir. Por defecto: todos los derechos reservados hasta que se defina si se libera bajo MIT, Apache-2.0 o licencia restringida (en caso de adopcion institucional).

## Autores

- Master Juan Alejandro Herrera Lopez — alejandroherreracr@gmail.com
- Andres Herrera Monge, CEO Mivisor — andres.herrera@mivisor.com
- Claude (Anthropic AI assistant) — co-autor de implementacion (codigo, schema, SDKs)
