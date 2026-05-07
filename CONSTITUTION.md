# CONSTITUTION.md — stellar_repo

Constitución del proyecto. Maxima autoridad **dentro de este repositorio** según la jerarquia de precedencia definida en el CLAUDE.md global del responsable técnico (R36):

```
CONSTITUTION.md (este archivo)  >  CLAUDE.md global  >  CLAUDE.md local  >  Spec  >  Contratos JSON  >  Código
```

Toda spec posterior debe abrir con una seccion **"Cumplimiento constitucional"** que enumere como respeta las clausulas no-negociables aquí listadas.

---

## 1. Stack tecnologico no-negociable

| Capa | Tecnología |
|------|------------|
| Blockchain | Stellar mainnet (testnet en desarrollo) |
| Smart contracts | Soroban (Rust + WASM) |
| SDK off-chain | `@stellar/stellar-sdk` (TypeScript) y/o `stellar-sdk` (Python) |
| Backend de servicios | FastAPI (Python) o Node + Express; elección final por spec |
| Base de datos off-chain | PostgreSQL gestionado. Proveedor concreto, instancia y reglas de compartición se definen en el CLAUDE.md local del proyecto. |
| Hosting | Container hosting gestionado. Proveedor concreto, proyecto/cuenta y región se definen en el CLAUDE.md local del proyecto. |
| Secretos | Gestor de secretos del proveedor de hosting (definido en CLAUDE.md local). **Prohibido hardcodear claves Stellar, API keys o credenciales en código o en `.env` versionado.** |
| Identidad de firmantes humanos | Firma digital del MICITT (CR) o equivalente reconocido legalmente, mapeada a llaves Stellar via DID |
| IA / modelos | Modelo y prompt versionados; idealmente reproducibles. Cada inferencia anclada con hash de modelo + hash de prompt + hash de input + hash de output. |

Cambiar de blockchain o de SDK requiere enmienda formal a esta Constitución.

## 2. Arquitectura no-negociable

- **Separacion estricta on-chain / off-chain.** On-chain solo: hashes, autorizaciones, eventos auditables, balances de assets. Off-chain: datos crudos (PDFs, fotos, modelos BIM, reportes IA completos) almacenados en object storage gestionado (S3-compatible, GCS, Azure Blob o equivalente) o IPFS, referenciados por CID/URL + hash.
- **La IA nunca es autoridad final.** Todo evento que dispare liberacion de fondos o publicación oficial requiere firma humana adicional. La IA es una de N firmas, nunca M-de-M con N=1.
- **El gemelo de transparencia no sustituye el sistema bancario.** El sistema legal de Tesoreria/SINPE permanece como fuente de verdad para flujos de valor reales. La cadena espeja eventos, no los reemplaza, salvo en escrows piloto explicitamente autorizados.
- **Multisig obligatorio para wallets institucionales.** Wallets que controlan fondos públicos o emision de assets deben ser M-de-N con M >= 2, custodiadas en hardware (Ledger/HSM) o en proveedores institucionales (Anchorage, Fireblocks).
- **Viewer público obligatorio.** No se considera completa ninguna etapa sin una interfaz web pública que permita a un ciudadano no técnico consultar el estado de cualquier obra y verificar hashes.

## 3. Datos y seguridad

- **Cero credenciales en código (R1 global).** Pre-commit obligatorio que detecte llaves privadas Stellar (S...), API keys y service accounts.
- **Privacidad por defecto.** Datos personales de funcionarios, contratistas o ciudadanos no se publican on-chain ni off-chain en claro. Solo hashes; los datos crudos viven en almacenamiento controlado con autorización.
- **Auditabilidad total.** Toda transacción on-chain debe poder rastrearse a (a) un evento de negocio off-chain, (b) un firmante identificable, y (c) una justificacion legal o técnica.
- **Region de datos:** la región por defecto del despliegue se especifica en el CLAUDE.md local del proyecto. Datos personales de ciudadanos CR pueden requerir residencia local; revisar caso a caso.
- **KYC/AML:** wallets de contratistas y de inversionistas en bonos tokenizados requieren verificación via SEP-12 o equivalente reconocido por SUGEF.

## 4. Calidad

- **Spec-driven (R36).** Sin spec aprobada no se escribe código. Hotfix triviales pueden usar spec-light, pero nunca saltar la spec.
- **Contrato API antes de paralelo (R37).** Si frontend y backend se desarrollan en paralelo, contrato JSON definido y compartido antes.
- **Tests obligatorios:**
  - Contratos Soroban: tests unitarios con `soroban-sdk` test framework, cobertura minima 80% de paths.
  - Servicios off-chain: tests de integración contra testnet Stellar antes de promocion a mainnet.
  - Reconciliacion: test diario que verifica consistencia entre datos on-chain y fuente oficial (Hacienda/SICOP cuando aplique).
- **Naming:** `snake_case` en Rust y Python, `camelCase` en JS/TS, `kebab-case` en archivos de spec.
- **Documentación:** cada contrato Soroban tiene su README en el subdirectorio del contrato + ejemplos de invocacion via `soroban contract invoke`.

## 5. Roles y modelo de usuarios

| Rol | Responsabilidad | Llave Stellar |
|-----|-----------------|---------------|
| Emisor / Banco de desarrollo | Emite assets, controla escrow, recibe repagos | Multisig institucional con hardware |
| Ente público ejecutor (municipio, MOPT) | Anclaje de eventos de obra, autorización de hitos | Multisig institucional |
| Auditor independiente | Firma de validación de hitos | Llave individual con DID verificada |
| Inspector técnico | Firma de inspeccion de obra | Llave individual con DID verificada |
| Validador IA | Genera reporte y lo firma | Llave de servicio (rotada periodicamente) |
| Contratista | Recibe desembolsos, ancla evidencia de avance | Wallet con KYC SEP-12 |
| Ciudadano observador | Consulta pública, opcional ancla observaciones | Sin llave (lectura) o llave pseudonima (escritura con anti-sybil) |
| CGR / supervisor | Lectura privilegiada, capacidad de iniciar disputas | Multisig institucional |

## 6. Reglas de negocio codificadas

- **Liberacion de fondos siempre M-de-N con M >= 2 firmantes humanos.** La firma de IA cuenta como insumo, no como una de las firmas requeridas.
- **Ventana de veto ciudadano:** entre autorización de pago y desembolso debe transcurrir un plazo configurable (recomendado 5-10 días habiles) durante el cual ciudadanos o CGR pueden iniciar disputa.
- **Trazabilidad obligatoria:** cada autorización de pago referencia (a) hash de reporte IA, (b) hashes de evidencia (foto, BIM, PDF), (c) firmas humanas, (d) hito del cronograma. Sin la cadena completa, el contrato rechaza la operación.
- **Penalidades automáticas:** atrasos respecto al cronograma generan descuentos automáticos del tranche correspondiente según formula definida en el contrato de adjudicacion.
- **Devolucion de remanentes:** al cierre de obra, cualquier saldo no liberado retorna automáticamente al emisor.
- **Reversibilidad limitada por clawback:** wallets emitidas usan `AUTH_CLAWBACK_ENABLED` durante el periodo de garantía, para permitir reversiones por orden judicial sin discusion técnica.

## 7. Operación

- **Observabilidad:**
  - Eventos on-chain monitoreados via Soroban RPC + Horizon.
  - Servicios off-chain con logs estructurados al sistema de logging gestionado del proveedor de hosting (definido en CLAUDE.md local).
  - Dashboard público con métricas agregadas (obras activas, fondos comprometidos, fondos liberados, tasa de validación IA).
- **Backups:**
  - Datos off-chain (object storage): replicacion multi-region.
  - Estado on-chain: irrelevante (la cadena es el backup), pero se mantiene snapshot diario para auditoria.
- **Presupuesto operativo:**
  - Costos Stellar: despreciables (~USD 1-10/mes incluso con miles de eventos).
  - Costos de infraestructura gestionada (container hosting + PostgreSQL gestionado + object storage): estimado USD 50-200/mes en piloto. Proveedor concreto y desglose en CLAUDE.md local del proyecto.
  - Costos de custodia institucional (HSM, Anchorage, etc.): a negociar según adopcion.

## 8. Gobernanza y proceso de enmienda

- **Autores y firmantes:**
  - Master Juan Alejandro Herrera Lopez <alejandroherreracr@gmail.com> — autor principal, a **titulo personal**.
  - Andres Herrera Monge, CEO Mivisor <andres.herrera@mivisor.com> — co-autor.
  - Claude (Anthropic AI assistant) <noreply@anthropic.com> — co-autor de implementación (código, schema, sdks).
- Esta Constitución rige una **propuesta de autores**; carece de respaldo institucional formal hasta que un endorser (CGR, MIDEPLAN, BCIE u otro) la suscriba. Mientras tanto, el repo es trabajo de los autores sin comprometer a ninguna entidad pública o privada.
- **Enmienda menor** (clarificacion, no cambio de stack ni de regla de negocio): commit firmado del responsable técnico.
- **Enmienda mayor** (cambio de blockchain, cambio de regla de liberacion de fondos, cambio de roles): requiere (a) propuesta documentada en `docs/enmiendas/`, (b) revision de al menos un asesor externo (legal o técnico según la naturaleza), (c) merge a `main` solo después de aprobacion explicita.
- **En caso de adopcion institucional** (BCIE, Banco Popular, CGR, etc.), la entidad adoptante puede sumar firmantes a la Constitución y exigir clausulas adicionales, sin contradecir las existentes.

## 9. Lo que esta Constitución **no** decide

- Si el bono tokenizado se denomina en USD, CRC o canasta. (Ver Etapa 3 de roadmap.)
- Cuanto dura la ventana de veto ciudadano exactamente. (Configurable por proyecto.)
- Si los datos sensibles se cifran con AES-256 o ChaCha20. (Elección técnica de spec.)
- Si el viewer público se construye en Next.js o en otro stack. (Elección técnica de spec.)

Estas decisiones son de **spec**, no constitucionales.

## 10. Hoja de fases

El sistema se construye en tres fases secuenciales, precedidas por un componente externo (Fase 0) que provee los insumos. La definición operativa, hitos y cronograma viven en `docs/09_roadmap_etapas.md`; aquí se define lo **normativo** de cada fase.

### Fase 0 — dIAra (sistema externo, fuera del alcance de este repo)

Plataforma independiente que captura imagenes desde obra pública via IoT, las analiza con LLMs multimodales y produce datos procesados (avance, personal, equipo, EPP, condiciones meteorologicas, accesibilidad universal). dIAra ya está desplegada en casos de uso reales (Circunvalacion de San Jose / puente Maria Aguilar en cooperación con LanammeUCR; Escuela de Limoncito del MEP).

dIAra **no vive en este repositorio**. Su integridad como proveedor de insumos es responsabilidad de su propio gobierno; este repositorio solo consume sus outputs y los firma con la llave Stellar designada como "validador IA" (ver §5). Toda spec de Fase 1 debe definir explicitamente las garantías de integridad exigidas a dIAra como condición de aceptacion de sus datos.

### Fase 1 — Anclaje en Stellar

Anclar en blockchain Stellar los hashes y metadatos de los datos+imagenes producidos por dIAra, como evidencia notarizada de obra. La cadena solo guarda hashes; los datos crudos viven en object storage gestionado o IPFS, referenciados por CID/URL.

- **Técnica primaria:** transacciones Stellar nativas (`manageData` o memo con hash). **Soroban no se utiliza en esta fase.**
- **Sin dinero on-chain. Sin smart contracts. Sin alertas.** Solo notarizacion auditable.
- **Promocion a mainnet** solo después de minimo 90 días de operación estable en testnet con datos reales.

### Fase 2 — Gemelo de transparencia

Extiende Fase 1 incluyendo:

- **Registro de eventos de pago.** Anclaje on-chain de hashes y metadatos de ordenes de pago de SICOP, hitos contractuales, autorizaciones de Hacienda y desembolsos efectivos de Tesoreria/SINPE, via oraculos.
- **Alertas via smart contracts Soroban.** Contratos consultivos que emiten eventos públicos on-chain cuando detectan inconsistencias (pago autorizado sin evidencia dIAra previa, hito completo sin hashes de respaldo, atrasos respecto a cronograma, anomalías en montos).
- **Las alertas son una señal, no gatillan acciones procedimentales.** Su destinatario natural es CGR; pueden replicarse a ciudadanía via dashboard público.
- **Sin dinero on-chain todavia.** Riesgo regulatorio minimo.
- **Protocolo de rectificacion obligatorio antes del primer despliegue:** como se modera, como se rectifica y quien responde legalmente cuando una alerta resulta ser falso positivo. Sin este protocolo aprobado, no hay despliegue de Fase 2.

### Fase 3 — Tokenizacion plena

Bono tokenizado emitido por un banco de desarrollo (BCIE, Banco Popular u otro) para financiar obra pública con auditabilidad continua. Diseñada como **piloto pequeño**: un solo proyecto, monto acotado, un solo tranche o pocos tranches, una sola jurisdiccion (preferiblemente municipal antes que gobierno central).

- Reusa los smart contracts de alertas de Fase 2 como validadores de liberacion de fondos.
- Aplican las reglas 6 ya establecidas (M-de-N con M >= 2 firmantes humanos, ventana de veto ciudadano, trazabilidad obligatoria, penalidades automáticas, devolucion de remanentes, clawback durante garantía).
- Requiere: anchor CRC<->Stellar (o uso de USDC), KYC SEP-12 de contratistas, custodia institucional (Anchorage, Fireblocks, HSM o equivalente), aprobacion regulatoria SUGEF/BCCR/SUGEVAL.

### Fase 2.5 — Escrow piloto (fallback)

**Solo si transcurridos 18 meses desde la promocion a mainnet de Fase 1 no se ha logrado partner bancario formal para Fase 3**, se considera un escrow piloto como paso intermedio: retencion en multisig Stellar de un porcentaje pequeño (5-10%) de pagos del Estado a contratistas, sin emision de deuda, eventualmente con cooperante internacional aportando USDC. **El fallback no es plan A.** Su existencia formal en esta Constitución es para no detener el proyecto si el escenario regulatorio o institucional impide Fase 3 en plazo razonable.

### Por que estas fases

- dIAra como Fase 0 externa preserva separacion de responsabilidades: la generacion de evidencia (visión por computador + IoT) es un dominio distinto al anclaje y financiamiento on-chain.
- Fase 1 sin Soroban evita sobreingenieria temprana y permite operación estable a costo despreciable.
- Fase 2 sin dinero on-chain evita riesgo regulatorio durante la fase de demostracion del valor de transparencia.
- Saltar Fase 2.5 y diseñar Fase 3 directamente como bono pequeño evita pagar dos veces el costo regulatorio para un solo resultado.

---

**Versión:** 0.3 (2026-05-06) — neutraliza referencias a proveedor de cloud específico en §1, §3, §7 y §10; los bindings concretos (proveedor, proyecto/cuenta, instancia, region, buckets, secretos) se mueven al `CLAUDE.md` local del repositorio. Sin cambios de stack constitucional (PostgreSQL, container hosting gestionado y object storage permanecen como elecciones no-negociables; Stellar+Soroban inalterado).
**Versión anterior:** 0.2 (2026-05-02) — agrega §10 Hoja de fases; aclara titularidad personal en §8.
**Versión anterior:** 0.1 (borrador inicial, 2026-04-30).
**Aprobacion:** Pendiente de revision con interlocutor institucional. Mientras tanto, vigente como propuesta del autor a titulo personal.
