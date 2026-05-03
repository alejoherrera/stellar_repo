# stellar_repo

Documentacion conceptual y de arquitectura para el uso de **Stellar** y **Soroban** como infraestructura de transparencia, monitoreo y financiamiento de **obra publica en Costa Rica**, integrando IA, validacion ciudadana y banca de desarrollo.

## Estado

**Pre-codigo / fase de exploracion conceptual.** Este repo recoge el resultado de una sesion de exploracion del 2026-04-29 / 2026-04-30. Aun no contiene contratos Soroban ni servicios desplegados. Es la base sobre la que se levantaran specs ejecutables (ver `docs/specs/`).

## Idea en una linea

Una arquitectura por etapas que parte de un **gemelo on-chain de transparencia** sobre el flujo de pagos publicos, evoluciona hacia **escrow programable con liberacion por hitos validados (IA + auditores + ciudadania)**, y culmina en un **bono tokenizado emitido por un banco de desarrollo** para financiar obra publica con auditabilidad continua.

## Alcance

- Caso de uso: obra publica en Costa Rica (gobierno central, municipalidades, infraestructura financiada por banca de desarrollo).
- Audiencia tecnica: ingenieria de blockchain (Stellar/Soroban) y backend (Python/JS).
- Audiencia institucional: CGR, BCIE, SUGEVAL, SUGEF, BCCR, Banco Popular, IFAM, MOPT, municipalidades, cooperacion internacional (BID, Banco Mundial).

## Indice de documentos

1. [Motivacion y contexto](docs/01_motivacion_y_contexto.md) — el problema que se busca resolver y por que Stellar.
2. [Casos de uso](docs/02_casos_de_uso.md) — desde notarizacion pasiva hasta bono tokenizado.
3. [Arquitectura propuesta](docs/03_arquitectura_propuesta.md) — capas on-chain y off-chain, integracion con sistema bancario tradicional.
4. [Comparativa de blockchains](docs/04_comparativa_blockchains.md) — Stellar vs Hedera HCS vs Polygon/EAS vs Algorand vs Arweave.
5. [Validacion ciudadana](docs/05_validacion_ciudadana.md) — cuatro capas y limitaciones honestas.
6. [Tokenizacion y banco de desarrollo](docs/06_tokenizacion_banco_desarrollo.md) — cinco variantes de instrumento y precedentes internacionales.
7. [Interoperabilidad bancaria](docs/07_interoperabilidad_bancaria.md) — SEPs, anchors, gap costarricense.
8. [Marco regulatorio CR](docs/08_marco_regulatorio_cr.md) — SUGEVAL, SUGEF, Ley 7732, Ley 7428.
9. [Roadmap por etapas](docs/09_roadmap_etapas.md) — Etapa 1 (gemelo) -> Etapa 2 (escrow) -> Etapa 3 (bono).
10. [Dudas pendientes](docs/10_dudas_pendientes.md) — preguntas R40 sin responder antes de avanzar.

## Specs

- [Etapa 1 — Gemelo de obra publica](docs/specs/2026-04-30_etapa1_gemelo_obra_publica.md) — primer paso construible, sin tokenizacion real.

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

## Contacto

Master Juan Alejandro Herrera Lopez — alejandroherreracr@gmail.com
