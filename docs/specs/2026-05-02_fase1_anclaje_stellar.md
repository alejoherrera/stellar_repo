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
  -> ipfs_client.pin(canonical_json) -> json_CID
  -> hash canonico del JSON
  -> persist en anchor.output (idempotente por output_id)
  -> stellar_signer.build_tx con multiples manageData (ver "Schema on-chain")
  -> stellar_client.submit(testnet|mainnet)
  -> persist en anchor.transaction
  -> verificar recuperabilidad de los CIDs via gateway publico (sanity check)
  -> retry exponencial en fallos de submission o pinning; alerta tras 5 fallos
```

### Schema on-chain (v2)

Cada output de dIAra se ancla en una sola TX Stellar con multiples operaciones `manageData`. Stellar limita cada `manageData` a 64 bytes en `key` y 64 bytes en `value`, por lo que se descompone la informacion del output en operaciones tematicas:

| Key (UTF-8) | Value | Proposito |
|-------------|-------|-----------|
| `diara:{output_id}` | `SHA256(json_canonico) (32B) || SHA256(imagen) (32B)` = 64 bytes | Prueba de integridad |
| `diara:{output_id}:proj` | codigo de proyecto, ej. `circunvalacion-cr` | Adscripcion al proyecto |
| `diara:{output_id}:dt` | fecha/hora original del JSON, truncada a 64B | Timestamp original |
| `diara:{output_id}:workers` | cantidad de personas, como string | Metadato consultable |
| `diara:{output_id}:machinery` | lista de maquinaria separada por coma, truncada a 64B | Metadato consultable |
| `diara:{output_id}:phase` | etapa constructiva, truncada a 64B | Metadato consultable |

Memo de la TX: `dIAra ancla v2`.

Adicionalmente, **una TX one-time de setup por proyecto** registra metadata de proyecto:

| Key (UTF-8) | Value | Proposito |
|-------------|-------|-----------|
| `proj:{code}:name` | nombre legible del proyecto | Identificacion |
| `proj:{code}:partner` | contraparte / cooperante (ej. `LanammeUCR`) | Trazabilidad institucional |
| `proj:{code}:url` | URL publica del monitoreo (ej. `obrapublica.info/ciudadania`) | Acceso ciudadano |
| `proj:{code}:system` | sistema productor de los datos (`dIAra`) | Adscripcion del proveedor |

Memo de la TX: `dIAra setup v1`.

**Por que multi-op y no un solo manageData con todo:** la limitacion de 64 bytes por value impide meter el JSON entero. Hashear todo en un solo blob (como hacia v1) preserva integridad pero deja al ciudadano dependiendo de tener acceso al JSON original para entender que paso. Con multi-op, el explorer publico de Stellar muestra los metadatos legibles directamente y la integridad criptografica sigue garantizada por la primera operacion (`diara:{output_id}` con los hashes).

**Por que no Soroban en Fase 1 a pesar del multi-op:** sigue siendo barato (~6 ops * 100 stroops = 600 stroops por output) y simple. Soroban entra en Fase 2 cuando aparecen alertas y reglas, no cuando solo se quiere mas estructura.

**Nota sobre IPFS:** una vez activo el pinning service, los CIDs (de imagen y de JSON canonico) se anclan via dos operaciones adicionales (`diara:{output_id}:img_cid` y `diara:{output_id}:json_cid`) que reemplazan o complementan los hashes en `diara:{output_id}` segun la conveniencia operativa. El PoC actual aun no integra IPFS.

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

## PoC implementado (2026-05-02)

Antes del desarrollo del servicio completo, se ejecuto un PoC en `scripts/anchor_demo.py` que implementa el subset minimo del flujo descrito arriba para validar el end-to-end Stellar:

**Subset implementado:**
- Lectura de JSONs estandarizados de dIAra (`diara_circunvalacion_json/json_test_estandarizado/`).
- Calculo de hash canonico SHA-256 del JSON y SHA-256 de la imagen JPG correspondiente.
- Submission de TX testnet siguiendo el "Schema on-chain (v2)" definido arriba.
- Setup TX one-time del proyecto `circunvalacion-cr`.
- Log JSON de cada corrida con tx_hash, ledger, hashes y URL del explorer.

**No implementado en el PoC** (deferido a anchor-service completo):
- IPFS pinning.
- DB PostgreSQL (`mivisor-db` esquema `anchor`).
- Webhook con firma Ed25519 de dIAra.
- Reconciler diario.
- Cloud Run deployment.

**Evidencia testnet (2026-05-03):**

Cuenta anchoring: `GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR`
- Explorer: https://stellar.expert/explorer/testnet/account/GDRWQERI6PI3WICTGPJBFBEFRV7ZRLCWG3IRA2YZQA5ZINHPY23JCPFR

Setup TX (proyecto `circunvalacion-cr`):
- `d7fd1582de3bbe81d73bc1d885079c681dd1a64b4970da3e66b5008b74f7e3f6`

Output anchor TXs (v2, una por output):
- `20251029-060211`: `20b5be0ca950c26217c9aada6b294ab9703c0129fe227fb93d9b0d37f90fc4ea`
- `20251029-175920`: `4d33baad1712f8b60f262628a7d2580e1072bc7eb4dcc9007de0ee95ff582bbc`
- `20251129-095756`: `2b9ced28102b3475627948f41d5a2f4fa22c96e5478f18e8eee3df2fdfd908d5`
- `20251129-124015`: `e15cd270d4235e3c935a421654a844ca1df16fd490928fab6fc987ff5b56e0be`
- `20251129-152245`: `8357a402bcd6a660f981b3926d6b9052d3c5fa22d25e9fce2e553ddc959272a4`
- `20251129-175905`: `ad1fa6e9e1b16f107246850284bae8592be5af25b93917910234bf717aa29cfb`

Existen ademas anclas v1 anteriores (formato single-op, 6 keys) en la misma cuenta. Las v2 las complementan agregando los metadatos legibles sin sobreescribir la prueba de integridad.

Logs en `scripts/anchors_log_*.json` (commiteados).

---

**Estado:** Borrador para revision. Schema on-chain validado en testnet.
**Autor:** Master Juan Alejandro Herrera Lopez, a titulo personal.
**Fecha:** 2026-05-02.
**Ultima actualizacion:** 2026-05-03 (schema v2 + evidencia PoC testnet).
**Constitution version requerida:** >= 0.2.
