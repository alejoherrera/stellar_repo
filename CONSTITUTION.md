# CONSTITUTION.md — stellar_repo

Constitucion del proyecto. Maxima autoridad **dentro de este repositorio** segun la jerarquia de precedencia definida en el CLAUDE.md global del responsable tecnico (R36):

```
CONSTITUTION.md (este archivo)  >  CLAUDE.md global  >  CLAUDE.md local  >  Spec  >  Contratos JSON  >  Codigo
```

Toda spec posterior debe abrir con una seccion **"Cumplimiento constitucional"** que enumere como respeta las clausulas no-negociables aqui listadas.

---

## 1. Stack tecnologico no-negociable

| Capa | Tecnologia |
|------|------------|
| Blockchain | Stellar mainnet (testnet en desarrollo) |
| Smart contracts | Soroban (Rust + WASM) |
| SDK off-chain | `@stellar/stellar-sdk` (TypeScript) y/o `stellar-sdk` (Python) |
| Backend de servicios | FastAPI (Python) o Node + Express; eleccion final por spec |
| Base de datos off-chain | PostgreSQL en Cloud SQL (instancia compartida `mivisor-db` del Universo A salvo justificacion explicita) |
| Hosting | Google Cloud Run en proyecto `nifty-province-474317-m0` (Universo A); region `us-east1` |
| Secretos | Google Secret Manager. **Prohibido hardcodear claves Stellar, API keys o credenciales en codigo o en `.env` versionado.** |
| Identidad de firmantes humanos | Firma digital del MICITT (CR) o equivalente reconocido legalmente, mapeada a llaves Stellar via DID |
| IA / modelos | Modelo y prompt versionados; idealmente reproducibles. Cada inferencia anclada con hash de modelo + hash de prompt + hash de input + hash de output. |

Cambiar de blockchain o de SDK requiere enmienda formal a esta Constitucion.

## 2. Arquitectura no-negociable

- **Separacion estricta on-chain / off-chain.** On-chain solo: hashes, autorizaciones, eventos auditables, balances de assets. Off-chain: datos crudos (PDFs, fotos, modelos BIM, reportes IA completos) almacenados en GCS o IPFS, referenciados por CID/URL + hash.
- **La IA nunca es autoridad final.** Todo evento que dispare liberacion de fondos o publicacion oficial requiere firma humana adicional. La IA es una de N firmas, nunca M-de-M con N=1.
- **El gemelo de transparencia no sustituye el sistema bancario.** El sistema legal de Tesoreria/SINPE permanece como fuente de verdad para flujos de valor reales. La cadena espeja eventos, no los reemplaza, salvo en escrows piloto explicitamente autorizados.
- **Multisig obligatorio para wallets institucionales.** Wallets que controlan fondos publicos o emision de assets deben ser M-de-N con M >= 2, custodiadas en hardware (Ledger/HSM) o en proveedores institucionales (Anchorage, Fireblocks).
- **Viewer publico obligatorio.** No se considera completa ninguna etapa sin una interfaz web publica que permita a un ciudadano no tecnico consultar el estado de cualquier obra y verificar hashes.

## 3. Datos y seguridad

- **Cero credenciales en codigo (R1 global).** Pre-commit obligatorio que detecte llaves privadas Stellar (S...), API keys y service accounts.
- **Privacidad por defecto.** Datos personales de funcionarios, contratistas o ciudadanos no se publican on-chain ni off-chain en claro. Solo hashes; los datos crudos viven en almacenamiento controlado con autorizacion.
- **Auditabilidad total.** Toda transaccion on-chain debe poder rastrearse a (a) un evento de negocio off-chain, (b) un firmante identificable, y (c) una justificacion legal o tecnica.
- **Region de datos:** us-east1 por defecto (Universo A). Datos personales de ciudadanos CR pueden requerir residencia local; revisar caso a caso.
- **KYC/AML:** wallets de contratistas y de inversionistas en bonos tokenizados requieren verificacion via SEP-12 o equivalente reconocido por SUGEF.

## 4. Calidad

- **Spec-driven (R36).** Sin spec aprobada no se escribe codigo. Hotfix triviales pueden usar spec-light, pero nunca saltar la spec.
- **Contrato API antes de paralelo (R37).** Si frontend y backend se desarrollan en paralelo, contrato JSON definido y compartido antes.
- **Tests obligatorios:**
  - Contratos Soroban: tests unitarios con `soroban-sdk` test framework, cobertura minima 80% de paths.
  - Servicios off-chain: tests de integracion contra testnet Stellar antes de promocion a mainnet.
  - Reconciliacion: test diario que verifica consistencia entre datos on-chain y fuente oficial (Hacienda/SICOP cuando aplique).
- **Naming:** `snake_case` en Rust y Python, `camelCase` en JS/TS, `kebab-case` en archivos de spec.
- **Documentacion:** cada contrato Soroban tiene su README en el subdirectorio del contrato + ejemplos de invocacion via `soroban contract invoke`.

## 5. Roles y modelo de usuarios

| Rol | Responsabilidad | Llave Stellar |
|-----|-----------------|---------------|
| Emisor / Banco de desarrollo | Emite assets, controla escrow, recibe repagos | Multisig institucional con hardware |
| Ente publico ejecutor (municipio, MOPT) | Anclaje de eventos de obra, autorizacion de hitos | Multisig institucional |
| Auditor independiente | Firma de validacion de hitos | Llave individual con DID verificada |
| Inspector tecnico | Firma de inspeccion de obra | Llave individual con DID verificada |
| Validador IA | Genera reporte y lo firma | Llave de servicio (rotada periodicamente) |
| Contratista | Recibe desembolsos, ancla evidencia de avance | Wallet con KYC SEP-12 |
| Ciudadano observador | Consulta publica, opcional ancla observaciones | Sin llave (lectura) o llave pseudonima (escritura con anti-sybil) |
| CGR / supervisor | Lectura privilegiada, capacidad de iniciar disputas | Multisig institucional |

## 6. Reglas de negocio codificadas

- **Liberacion de fondos siempre M-de-N con M >= 2 firmantes humanos.** La firma de IA cuenta como insumo, no como una de las firmas requeridas.
- **Ventana de veto ciudadano:** entre autorizacion de pago y desembolso debe transcurrir un plazo configurable (recomendado 5-10 dias habiles) durante el cual ciudadanos o CGR pueden iniciar disputa.
- **Trazabilidad obligatoria:** cada autorizacion de pago referencia (a) hash de reporte IA, (b) hashes de evidencia (foto, BIM, PDF), (c) firmas humanas, (d) hito del cronograma. Sin la cadena completa, el contrato rechaza la operacion.
- **Penalidades automaticas:** atrasos respecto al cronograma generan descuentos automaticos del tranche correspondiente segun formula definida en el contrato de adjudicacion.
- **Devolucion de remanentes:** al cierre de obra, cualquier saldo no liberado retorna automaticamente al emisor.
- **Reversibilidad limitada por clawback:** wallets emitidas usan `AUTH_CLAWBACK_ENABLED` durante el periodo de garantia, para permitir reversiones por orden judicial sin discusion tecnica.

## 7. Operacion

- **Observabilidad:**
  - Eventos on-chain monitoreados via Soroban RPC + Horizon.
  - Servicios off-chain con logs estructurados a Cloud Logging.
  - Dashboard publico con metricas agregadas (obras activas, fondos comprometidos, fondos liberados, tasa de validacion IA).
- **Backups:**
  - Datos off-chain (GCS): replicacion multi-region.
  - Estado on-chain: irrelevante (la cadena es el backup), pero se mantiene snapshot diario para auditoria.
- **Presupuesto operativo:**
  - Costos Stellar: despreciables (~USD 1-10/mes incluso con miles de eventos).
  - Costos GCP: estimado USD 50-200/mes para Cloud Run + Cloud SQL + GCS en piloto.
  - Costos de custodia institucional (HSM, Anchorage, etc.): a negociar segun adopcion.

## 8. Gobernanza y proceso de enmienda

- **Firmante actual:** Master Juan Alejandro Herrera Lopez (alejandroherreracr@gmail.com), a **titulo personal**. Esta Constitucion rige una **propuesta de autor**; carece de respaldo institucional formal hasta que un endorser (CGR, MIDEPLAN, BCIE u otro) la suscriba. Mientras tanto, el repo es trabajo del autor sin comprometer a ninguna entidad publica o privada.
- **Enmienda menor** (clarificacion, no cambio de stack ni de regla de negocio): commit firmado del responsable tecnico.
- **Enmienda mayor** (cambio de blockchain, cambio de regla de liberacion de fondos, cambio de roles): requiere (a) propuesta documentada en `docs/enmiendas/`, (b) revision de al menos un asesor externo (legal o tecnico segun la naturaleza), (c) merge a `main` solo despues de aprobacion explicita.
- **En caso de adopcion institucional** (BCIE, Banco Popular, CGR, etc.), la entidad adoptante puede sumar firmantes a la Constitucion y exigir clausulas adicionales, sin contradecir las existentes.

## 9. Lo que esta Constitucion **no** decide

- Si el bono tokenizado se denomina en USD, CRC o canasta. (Ver Etapa 3 de roadmap.)
- Cuanto dura la ventana de veto ciudadano exactamente. (Configurable por proyecto.)
- Si los datos sensibles se cifran con AES-256 o ChaCha20. (Eleccion tecnica de spec.)
- Si el viewer publico se construye en Next.js o en otro stack. (Eleccion tecnica de spec.)

Estas decisiones son de **spec**, no constitucionales.

## 10. Hoja de fases

El sistema se construye en tres fases secuenciales, precedidas por un componente externo (Fase 0) que provee los insumos. La definicion operativa, hitos y cronograma viven en `docs/09_roadmap_etapas.md`; aqui se define lo **normativo** de cada fase.

### Fase 0 — dIAra (sistema externo, fuera del alcance de este repo)

Plataforma independiente que captura imagenes desde obra publica via IoT, las analiza con LLMs multimodales y produce datos procesados (avance, personal, equipo, EPP, condiciones meteorologicas, accesibilidad universal). dIAra ya esta desplegada en casos de uso reales (Circunvalacion de San Jose / puente Maria Aguilar en cooperacion con LanammeUCR; Escuela de Limoncito del MEP).

dIAra **no vive en este repositorio**. Su integridad como proveedor de insumos es responsabilidad de su propio gobierno; este repositorio solo consume sus outputs y los firma con la llave Stellar designada como "validador IA" (ver §5). Toda spec de Fase 1 debe definir explicitamente las garantias de integridad exigidas a dIAra como condicion de aceptacion de sus datos.

### Fase 1 — Anclaje en Stellar

Anclar en blockchain Stellar los hashes y metadatos de los datos+imagenes producidos por dIAra, como evidencia notarizada de obra. La cadena solo guarda hashes; los datos crudos viven en GCS o IPFS, referenciados por CID/URL.

- **Tecnica primaria:** transacciones Stellar nativas (`manageData` o memo con hash). **Soroban no se utiliza en esta fase.**
- **Sin dinero on-chain. Sin smart contracts. Sin alertas.** Solo notarizacion auditable.
- **Promocion a mainnet** solo despues de minimo 90 dias de operacion estable en testnet con datos reales.

### Fase 2 — Gemelo de transparencia

Extiende Fase 1 incluyendo:

- **Registro de eventos de pago.** Anclaje on-chain de hashes y metadatos de ordenes de pago de SICOP, hitos contractuales, autorizaciones de Hacienda y desembolsos efectivos de Tesoreria/SINPE, via oraculos.
- **Alertas via smart contracts Soroban.** Contratos consultivos que emiten eventos publicos on-chain cuando detectan inconsistencias (pago autorizado sin evidencia dIAra previa, hito completo sin hashes de respaldo, atrasos respecto a cronograma, anomalias en montos).
- **Las alertas son una señal, no gatillan acciones procedimentales.** Su destinatario natural es CGR; pueden replicarse a ciudadania via dashboard publico.
- **Sin dinero on-chain todavia.** Riesgo regulatorio minimo.
- **Protocolo de rectificacion obligatorio antes del primer despliegue:** como se modera, como se rectifica y quien responde legalmente cuando una alerta resulta ser falso positivo. Sin este protocolo aprobado, no hay despliegue de Fase 2.

### Fase 3 — Tokenizacion plena

Bono tokenizado emitido por un banco de desarrollo (BCIE, Banco Popular u otro) para financiar obra publica con auditabilidad continua. Disenada como **piloto pequeño**: un solo proyecto, monto acotado, un solo tranche o pocos tranches, una sola jurisdiccion (preferiblemente municipal antes que gobierno central).

- Reusa los smart contracts de alertas de Fase 2 como validadores de liberacion de fondos.
- Aplican las reglas 6 ya establecidas (M-de-N con M >= 2 firmantes humanos, ventana de veto ciudadano, trazabilidad obligatoria, penalidades automaticas, devolucion de remanentes, clawback durante garantia).
- Requiere: anchor CRC<->Stellar (o uso de USDC), KYC SEP-12 de contratistas, custodia institucional (Anchorage, Fireblocks, HSM o equivalente), aprobacion regulatoria SUGEF/BCCR/SUGEVAL.

### Fase 2.5 — Escrow piloto (fallback)

**Solo si transcurridos 18 meses desde la promocion a mainnet de Fase 1 no se ha logrado partner bancario formal para Fase 3**, se considera un escrow piloto como paso intermedio: retencion en multisig Stellar de un porcentaje pequeño (5-10%) de pagos del Estado a contratistas, sin emision de deuda, eventualmente con cooperante internacional aportando USDC. **El fallback no es plan A.** Su existencia formal en esta Constitucion es para no detener el proyecto si el escenario regulatorio o institucional impide Fase 3 en plazo razonable.

### Por que estas fases

- dIAra como Fase 0 externa preserva separacion de responsabilidades: la generacion de evidencia (vision por computador + IoT) es un dominio distinto al anclaje y financiamiento on-chain.
- Fase 1 sin Soroban evita sobreingenieria temprana y permite operacion estable a costo despreciable.
- Fase 2 sin dinero on-chain evita riesgo regulatorio durante la fase de demostracion del valor de transparencia.
- Saltar Fase 2.5 y disenar Fase 3 directamente como bono pequeño evita pagar dos veces el costo regulatorio para un solo resultado.

---

**Version:** 0.2 (2026-05-02) — agrega §10 Hoja de fases; aclara titularidad personal en §8.
**Version anterior:** 0.1 (borrador inicial, 2026-04-30).
**Aprobacion:** Pendiente de revision con interlocutor institucional. Mientras tanto, vigente como propuesta del autor a titulo personal.
