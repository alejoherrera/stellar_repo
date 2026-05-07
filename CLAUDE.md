# CLAUDE.md — stellar_repo (instrucciones locales del proyecto)

Reglas y bindings específicos de este repositorio. Complementan al `CLAUDE.md` global del responsable técnico y a la `CONSTITUTION.md` de este repo.

Jerarquía de precedencia (R36 global): `CONSTITUTION.md` > CLAUDE.md global > **este archivo** > spec del feature > contratos JSON > código.

---

## Infraestructura concreta (bindings que la Constitución delega aquí)

La Constitución de este repo (`CONSTITUTION.md` §1, §3, §7) fija el **tipo** de infraestructura (PostgreSQL gestionado, container hosting gestionado, object storage gestionado, gestor de secretos del proveedor) pero deja al CLAUDE.md local la **encarnación concreta**. Para este repo, el binding actual es:

| Recurso | Valor concreto |
|---|---|
| Proveedor de cloud | Google Cloud Platform (GCP) |
| Cuenta / Workspace | Universo A del responsable técnico (`alejandroherrera@gmail.com`) |
| Project ID | `nifty-province-474317-m0` |
| Región default | `us-east1` |
| Container hosting | Google Cloud Run |
| PostgreSQL gestionado | Cloud SQL — instancia compartida `mivisor-db` (PostgreSQL 15). BD `mivisor` (prod) / `mivisor_staging`. Crear schema dedicado `stellar` o BD aparte si la spec lo justifica. |
| Object storage | Google Cloud Storage (GCS). Bucket dedicado a definir por spec (sugerido `stellar-evidence` / `stellar-evidence-staging`). |
| Secretos | Google Secret Manager. Llaves Stellar (`S...`), API keys de Horizon/Soroban RPC, service accounts. **Nunca en código ni en `.env` versionado.** |
| Logs | Cloud Logging (logs estructurados JSON). |
| CLI | `GCLOUD="/c/Users/aleja/AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin/gcloud"` |

Cambiar de proveedor de cloud no requiere enmienda constitucional (la Constitución es agnóstica), pero sí actualización de este archivo + spec de migración.

**Universo B (EUREKA / `eureka-493319` / Workspace `cgr.go.cr`) es proyecto institucional CGR distinto. Jamás mezclar con este repo.** Este binding es Universo A puro.

## Stellar — bindings de red

| Recurso | Valor |
|---|---|
| Red default en desarrollo | Stellar testnet (`Test SDF Network ; September 2015`) |
| Red de producción | Stellar mainnet (`Public Global Stellar Network ; September 2015`) — solo después de los 90 días de testnet estable que exige `CONSTITUTION.md` §10 Fase 1 |
| Horizon testnet | `https://horizon-testnet.stellar.org` |
| Horizon mainnet | `https://horizon.stellar.org` |
| Soroban RPC testnet | `https://soroban-testnet.stellar.org` |
| Llaves de servicio (validador IA, anclaje dIAra, etc.) | Generadas y custodiadas en Secret Manager. Nunca en repo. |

## Convenciones específicas del repo

- **Spec antes de código (R36 global).** Specs en `docs/specs/YYYY-MM-DD_nombre.md`. Las dos vigentes son `2026-05-02_fase1_anclaje_stellar.md` y `2026-05-02_fase2_gemelo_transparencia.md`.
- **Idioma:** español neutro con tildes correctas en docs y commits. Comentarios de código pueden ser inglés o español según contexto del módulo (Rust/Soroban tiende a inglés por idiomatismo del ecosistema).
- **Encoding (R5 global):** sin emojis en `print`/`logs`. Consola Windows = codepage 1252.
- **SDK JS:** `sdk/js/` publicado a npm como paquete propio (`@stellar-cr/sdk` o equivalente — confirmar nombre con cada release). Demos en `sdk/js/examples/`.
- **Dashboard / landing pública:** servida desde GitHub Pages en `stellar.mivisor.com`. Cambios al dashboard se prueban localmente antes de commit.

## Lo que NO se decide aquí

- Reglas de negocio (M-de-N, ventana de veto, clawback, penalidades) → `CONSTITUTION.md` §6.
- Stack de blockchain (Stellar/Soroban) → `CONSTITUTION.md` §1.
- Arquitectura on-chain/off-chain → `CONSTITUTION.md` §2.
- Procedimiento de enmienda → `CONSTITUTION.md` §8.

Esos son constitucionales y este archivo no puede contradecirlos.
