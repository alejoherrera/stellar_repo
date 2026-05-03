# [Fase 1] Anclaje en Stellar de outputs de dIAra

## Cumplimiento constitucional

Esta spec implementa la Fase 1 declarada en `CONSTITUTION.md` §10. Cumplimientos especificos:

- **§1 Stack:** Stellar (testnet primero, mainnet despues de 90 dias estables); backend FastAPI (Python); Cloud Run en `nifty-province-474317-m0`; Cloud SQL `mivisor-db`; **IPFS** (via servicio de pinning) para imagenes raw; Google Secret Manager para la llave Stellar del validador IA y credenciales del pinning service.
- **§2 Arquitectura:** separacion estricta on-chain / off-chain. La cadena solo guarda hashes y metadatos minimos; las imagenes raw permanecen en IPFS, identificadas por su CID (content-addressable, hash-based por construccion) y referenciadas desde la transaccion Stellar. El CID **es** el hash, lo que elimina la posibilidad de divergencia entre identificador y contenido.
- **§3 Datos y seguridad:** la llave Stellar del validador IA vive solo en Secret Manager; pre-commit hook detecta llaves Stellar (`S...`) y service accounts. No se anclan datos personales en claro.
- **§4 Calidad:** spec aprobada antes de codigo (R36). Contrato API entre dIAra y anchor-service definido antes de empezar (R37). Tests unitarios e integracion contra testnet con cobertura >= 80%.
- **§5 Roles:** este servicio actua como "Validador IA" segun la tabla de roles.
- **§10 Fase 1:** **NO se usa Soroban.** Solo transacciones Stellar nativas (`manageData` con hash). Promocion a mainnet solo tras 90 dias estables en testnet con criterios de exito cumplidos.

## Problema

dIAra (sistema externo) produce datos procesados e imagenes desde obras publicas (Circunvalacion / puente Maria Aguilar; Escuela de Limoncito). Hoy estos datos viven en obrapublica.info pero **no son verificables por terceros**: cualquier observador externo carece de forma criptografica de probar que un output no fue alterado retroactivamente. Sin un ancla en blockchain publica, dIAra es solo un dashboard de autor.

Para que el ecosistema (CGR, ciudadania, supervisores, contratistas, futuros inversionistas en Fase 3) pueda confiar en los datos, cada output de dIAra debe quedar anclado en blockchain con timestamp y firma verificable.

## Solucion propuesta

Servicio **anchor-service**: recibe via webhook los outputs de dIAra y por cada uno construye una transaccion Stellar (`manageData(key=cid_o_hash, value=metadata_min)` + memo). Persiste metadatos en PostgreSQL y pinea las imagenes raw en IPFS via un servicio de pinning.

### Componentes

1. **anchor-service** (Cloud Run, FastAPI): expone `POST /ingest` (webhook desde dIAra) y `GET /health`. Procesa cada output: valida firma -> persiste metadata -> pinea imagen en IPFS y obtiene CID -> construye TX Stellar -> firma -> submit -> persiste tx_hash. Idempotente por `output_id`.
2. **stellar-signer** (modulo interno): firma con la llave del validador IA leida de Secret Manager.
3. **ipfs-client** (modulo interno): pinea contenido via API del servicio elegido (Pinata, Web3.Storage, Filebase u otro); obtiene CID y verifica recuperabilidad via gateway publico.
4. **reconciler** (Cloud Run job, diario): compara outputs del dia vs transacciones registradas en DB y on-chain (Horizon), y verifica que cada CID anclado siga recuperable via al menos un gateway publico. Reporta divergencias.
5. **DB schema** `anchor`: tablas `obra`, `output`, `transaction`, `reconciliation_log` en `mivisor-db`.
6. **Pinning service**: contratado externamente (decision pendiente abajo). Adicionalmente, el sistema documenta el CID en chain de modo que cualquier tercero pueda re-pinear el contenido si lo desea (esa es la ventaja de IPFS).

### Flujo

```
dIAra output -> POST /ingest (firmado)
  -> validar firma de dIAra
  -> ipfs_client.pin(image) -> CID  (idempotente: si ya esta pineado, retorna mismo CID)
  -> hash de metadatos (canonical JSON)
  -> persist en anchor.output (idempotente por output_id)
  -> stellar_signer.build_tx(manageData(CID, metadata_hash) + memo)
  -> stellar_client.submit(testnet|mainnet)
  -> persist en anchor.transaction
  -> verificar recuperabilidad del CID via gateway publico (sanity check)
  -> retry exponencial en fallos de submission o pinning; alerta tras 5 fallos
```

**Nota sobre CID y hash:** el CID v1 de IPFS es la representacion estandar del hash multihash del contenido. Anclar el CID es equivalente a anclar el hash de la imagen, con la ventaja de que el CID es directamente resolvible en cualquier nodo IPFS sin esquema externo. Por eso usamos `manageData(key=CID)` en lugar de `manageData(key=image_hash)`.

### Garantias exigidas a dIAra (Fase 0)

Toda integracion requiere acuerdo formal:

- `output_id` unico y estable.
- `schema_version` obligatorio; outputs con esquema desconocido se rechazan con HTTP 400.
- Imagen raw entregable a anchor-service con su CID precalculado (o calculable de forma determinista por anchor-service); pinning durable garantizado por anchor-service durante minimo 7 anos.
- Firma Ed25519 de dIAra sobre `(output_id, schema_version, image_hash, metadata_hash, timestamp)`. Llave publica registrada en Secret Manager del lado de anchor-service.
- Procedimiento de invalidacion retroactiva: dIAra notifica via `POST /invalidate`; anchor-service marca el output como `invalidated_by_source=true` en DB pero **no borra la transaccion Stellar** (es inmutable). La invalidacion queda como hecho registrable adicional en proxima reconciliacion.

## Archivos afectados (creados)

```
anchor-service/
├── pyproject.toml
├── app/
│   ├── main.py
│   ├── ingest.py
│   ├── stellar_signer.py
│   ├── stellar_client.py
│   ├── ipfs_client.py
│   ├── db.py
│   └── reconciler.py
├── tests/
│   ├── test_ingest.py
│   ├── test_stellar_signer.py
│   ├── test_ipfs_client.py
│   ├── test_reconciler.py
│   └── fixtures/
├── infra/
│   ├── Dockerfile
│   └── cloudbuild.yaml
└── docs/
    ├── api_contract.json
    └── runbook.md
```

DB nuevas tablas en `mivisor-db` esquema `anchor`:

| Tabla | Campos clave |
|-------|--------------|
| `anchor.obra` | id, codigo, nombre, institucion, contratista, monto, fecha_inicio, fecha_fin, ubicacion |
| `anchor.output` | id, obra_id, output_id_diara (UNIQUE), schema_version, image_cid, metadata_hash, metadata_jsonb, ingested_at, invalidated_by_source |
| `anchor.transaction` | id, output_id (FK), network, tx_hash, ledger, fee_xlm, status, submitted_at, confirmed_at |
| `anchor.pin_status` | id, cid, pinning_provider, pinned_at, last_verified_at, gateway_reachable |
| `anchor.reconciliation_log` | id, run_date, outputs_checked, divergencias_count, divergencias_jsonb |

## Criterios de aceptacion

### Funcionales

1. Webhook con output valido produce: registro en `output` + imagen pineada en IPFS con CID + transaccion Stellar testnet exitosa + registro en `transaction`.
2. Webhook con `output_id` ya procesado retorna 200 sin generar transaccion duplicada ni nuevo pin (idempotente).
3. Webhook con `schema_version` desconocido retorna 400.
4. Webhook con firma invalida de dIAra retorna 401.
5. Imagen raw recuperable via cualquier gateway IPFS publico usando el CID anclado.
6. Toda transaccion on-chain es localizable en DB y viceversa.
7. Reconciler detecta y reporta cualquier output sin transaccion confirmada en > 24h, o cualquier CID que no responda en gateway publico.

### No funcionales

- Latencia ingesta -> tx submitted < 5 min p95.
- Costo por ancla < USD 0.001 promedio.
- Disponibilidad anchor-service: 99% testnet, 99.9% mainnet.
- 0 transacciones perdidas durante 30 dias consecutivos en testnet (criterio de promocion).
- Cobertura tests >= 80%.

### Criterios de promocion a mainnet

1. 90 dias estables en testnet con datos reales de minimo 5 obras.
2. Reconciliacion diaria con 0 divergencias durante 30 dias consecutivos.
3. Revision de seguridad de la llave validador-ia (rotacion documentada).
4. Sign-off explicito del autor.

## Decisiones pendientes

1. **Webhook vs pull:** webhook con retry o pull periodico desde anchor-service. Recomendacion: webhook. Pendiente confirmar con autor de dIAra.
2. **Formato de firma de dIAra:** Stellar nativo Ed25519 (uniforme) o JWT con clave separada. Recomendacion: Ed25519.
3. **Granularidad:** una TX por output (simple) o batching de N outputs en una TX (cheaper at scale). Recomendacion: una por output al inicio; evaluar batching cuando el volumen lo justifique.
4. **Servicio de pinning IPFS:** opciones evaluadas — Pinata (maduro, API simple, USD ~20/mes para piloto), Web3.Storage (gratis con limites, respaldo Filecoin), Filebase (S3-compatible, USD ~6/TB-mes), nodo IPFS auto-hospedado en GCP (control total, mas costo operativo). **Recomendacion: Pinata para piloto + verificar recuperabilidad cruzada via gateways publicos (ipfs.io, dweb.link).** Documentar el CID en chain de modo que cualquier tercero (CGR, ONG, ciudadania) pueda re-pinear si lo desea — esa es justamente la ventaja de IPFS sobre almacenamiento centralizado.
5. **Backup en GCS:** ¿pinear ademas en GCS como respaldo institucional, o confiar en IPFS + multi-pinning? Recomendacion: empezar solo IPFS; agregar GCS como backup frio si surge requisito institucional explicito.
6. **Schema versioning:** semver o secuencial entero. Recomendacion: semver `MAJOR.MINOR`.

## Riesgos

| Riesgo | Mitigacion |
|--------|------------|
| dIAra cambia esquema sin aviso | `schema_version` obligatorio + rechazo automatico de esquemas desconocidos |
| Llave validador-ia comprometida | Rotacion documentada + monitoreo de uso + alerta ante uso no esperado |
| Stellar testnet reset (puede ocurrir) | Documentado en runbook; re-ingesta automatizada de outputs no confirmados |
| Volumen pico de dIAra excede capacidad | Cloud Run autoscaling + cola interna (Pub/Sub si se requiere) |
| Imagenes pesadas elevan costos de pinning | Compresion antes de pin (target < 500KB por imagen); revisar tarifa de pinning provider |
| Pinning provider unico es punto de falla | Re-pinear via segundo provider tras N dias en mainnet; documentar CID publico facilita re-pin por terceros |
| Gateway publico de IPFS lento o caido | Reconciler verifica multiple gateways; CID anclado en chain garantiza que el contenido es recuperable de cualquier nodo IPFS |

## Tipo

Feature grande (10+ archivos, schema DB nuevo, integracion blockchain, integracion con sistema externo).

---

**Estado:** Borrador para revision.
**Autor:** Master Juan Alejandro Herrera Lopez, a titulo personal.
**Fecha:** 2026-05-02.
**Constitution version requerida:** >= 0.2.
