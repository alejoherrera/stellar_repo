# Roadmap por fases

Documento operativo. La definicion **normativa** de las fases vive en `CONSTITUTION.md` §10. Este documento agrega contexto, hitos concretos, criterios de exito, decisiones pendientes y dependencias.

## Resumen

| Fase | Que se construye | Dinero on-chain | Smart contracts | Riesgo regulatorio |
|------|------------------|-----------------|------------------|---------------------|
| 0 | dIAra (externa) — captura y analisis IA en obra | No | No | Ninguno |
| 1 | Anclaje en Stellar de evidencia de dIAra | No | No (transacciones nativas) | Ninguno |
| 2 | Gemelo de transparencia + alertas Soroban | No | Si (consultivos) | Bajo (legalmente sensible por alertas) |
| 3 | Bono tokenizado piloto | Si | Si (validadores de liberacion) | Alto (SUGEF/BCCR/SUGEVAL) |
| 2.5 (fallback) | Escrow piloto | Si (limitado) | Si | Medio |

## Fase 0 — dIAra (externa)

**Estado:** desplegada y operativa.

**URLs publicas:**
- https://www.obrapublica.info/ciudadania — Circunvalacion de San Jose / puente sobre rio Maria Aguilar, en cooperacion con LanammeUCR.
- https://www.obrapublica.info/limoncito — Escuela de Limoncito (MEP, Cieneguita de Limon), inversion ~US$15M, datos diarios desde febrero de 2026.
- https://www.obrapublica.info/blockchain — demo de eventos meteorologicos en blockchain publica (red Sepolia, Ethereum testnet).

**Lo que produce dIAra:** datos procesados por LLM multimodal + imagenes raw + metadatos (timestamp, georreferencia, hash, etiquetas estructuradas).

**Lo que se le exige como proveedor de insumos al stellar_repo:**
- Llave Stellar designada como "validador IA" para firmar sus outputs.
- SLA de disponibilidad y reproducibilidad del modelo (a definir en spec Fase 1).
- Almacenamiento durable de imagenes raw (GCS/IPFS) con CID/URL estable.
- Procedimiento documentado de incident response cuando un output es invalidado retroactivamente.

dIAra no vive en este repo. Su gobierno propio es responsabilidad de su autor; este repo solo consume sus outputs bajo las garantias listadas.

## Fase 1 — Anclaje en Stellar

**Objetivo:** que cualquier dato producido por dIAra tenga un ancla on-chain verificable por terceros.

**Hitos:**
1. Spec aprobada (R36) que defina formato de transaccion, manejo de errores, idempotencia y garantias exigidas a dIAra.
2. Llave Stellar de "validador IA" provisionada en Google Secret Manager.
3. Servicio de ingesta que toma outputs de dIAra y construye transacciones Stellar.
4. Despliegue en testnet con minimo 5 obras reales durante minimo 90 dias.
5. Reconciliacion diaria entre outputs de dIAra y anclas on-chain (test automatizado).
6. Promocion a mainnet con criterios de exito cumplidos.

**Criterios de exito para promover a mainnet:**
- 0 transacciones perdidas en testnet (idempotencia probada bajo fallos de red, restart, doble entrega).
- Costo por ancla < USD 0.001 promedio.
- Latencia ingesta -> ancla < 5 minutos en p95.
- Reconciliacion diaria con 0 divergencias durante 30 dias consecutivos.

**Tecnica:**
- Transacciones nativas Stellar (`manageData` con hash, o `payment` con memo). **No Soroban en esta fase.**
- Backend de ingesta: FastAPI (Python) o Express (Node), eleccion final por spec.
- Persistencia de metadata off-chain: PostgreSQL en Cloud SQL (`mivisor-db`).
- Imagenes raw: GCS bucket dedicado con clase Coldline tras 90 dias.

**Riesgos abiertos:**
- Que dIAra cambie su esquema de outputs sin previo aviso. Mitigacion: spec define versionado de esquema; el ingestor rechaza outputs con esquema desconocido.

## Fase 2 — Gemelo de transparencia

**Objetivo:** que cualquier ciudadano pueda recorrer la cadena completa contrato -> hito -> evidencia dIAra -> autorizacion de pago -> desembolso, y que el sistema emita alertas publicas cuando la cadena tenga huecos.

**Pre-requisitos no-tecnicos (deben validarse antes de spec):**
- **Acceso o oracle a SICOP** para eventos de adjudicacion y autorizacion. **Riesgo abierto:** factibilidad pendiente de validar.
- **Acceso o oracle a Hacienda/Tesoreria** para eventos de desembolso. **Riesgo abierto:** factibilidad pendiente de validar.
- **Protocolo de rectificacion de alertas** (legal). Sin esto no se despliega Fase 2.

**Hitos:**
1. Validar factibilidad de oraculos a SICOP y Hacienda. Si imposible, replantear scope.
2. Definir protocolo de rectificacion de alertas (moderacion, rectificacion, responsabilidad legal).
3. Spec aprobada con protocolo de rectificacion.
4. Smart contracts Soroban de alertas desplegados en testnet.
5. Dashboard publico con visualizacion de cadena por obra.
6. Pruebas legales del protocolo de rectificacion (caso ficticio de falso positivo).
7. Despliegue mainnet.

**Decisiones pendientes:**
- **Primer destinatario de alertas:** ¿solo CGR (privado), o publico desde el inicio? Recomendacion provisional: privado a CGR durante 6 meses, despues evaluar publicacion.
- **Granularidad de alertas:** ¿una alerta por inconsistencia, o agregadas semanalmente? Mas granular = mas señal y mas ruido.
- **Modelo de costos a escala:** Soroban tiene rent fees; modelar a 10K obras x N alertas/dia antes de mainnet.

**Tipos de inconsistencia inicial (ampliable por spec):**
- Pago autorizado sin evidencia dIAra previa.
- Hito marcado completo sin hashes de respaldo.
- Atrasos respecto a cronograma del contrato.
- Anomalias en montos (pago > monto del hito).
- Personal/equipo en obra cae a cero por mas de N dias sin reporte de suspension.

## Fase 3 — Bono tokenizado piloto

**Objetivo:** financiar una obra publica concreta via bono tokenizado con liberacion programable validada por la cadena.

**Pre-requisitos no-tecnicos:**
- Partner bancario formal (BCIE, Banco Popular u otro). **Sin partner, no hay Fase 3.**
- Aprobacion regulatoria SUGEF/BCCR/SUGEVAL.
- Anchor CRC<->Stellar operativo (o decision de usar USDC).
- Custodia institucional contratada (Anchorage, Fireblocks, HSM propio).
- Convenio multipartito: emisor + ente publico ejecutor + auditor + contratista.

**Alcance del piloto:**
- Una sola obra.
- Monto < USD 2M.
- Un solo tranche o pocos tranches.
- Una sola jurisdiccion (recomendado: una municipalidad piloto antes que gobierno central).

**Hitos:**
1. Identificar partner bancario y obra piloto.
2. Spec del instrumento financiero (tasa, plazo, denominacion, garantias, perfil de inversionista).
3. Aprobacion regulatoria.
4. Smart contracts de bono y escrow desplegados (reusan validadores de Fase 2).
5. Emision de assets, on-ramping de inversionistas KYC SEP-12.
6. Ejecucion del piloto durante el plazo del bono.
7. Repago y cierre.

## Fase 2.5 — Escrow piloto (fallback)

**Activacion:** si transcurridos 18 meses desde promocion a mainnet de Fase 1 no se ha asegurado partner bancario formal para Fase 3.

**Diferencia con Fase 3:** no hay emision de deuda. Solo retencion en multisig Stellar de un porcentaje pequeño (5-10%) de pagos del Estado a contratistas, liberable al cumplirse hitos validados por los contratos de Fase 2.

**Partner posible:** una municipalidad + cooperante internacional (BID, GIZ) que aporte USDC.

**Razon de existir formal:** mantener avance del proyecto si el escenario regulatorio o institucional impide Fase 3 en plazo razonable. No es plan A.

## Riesgos transversales

| Riesgo | Mitigacion |
|--------|------------|
| Sin endorso institucional, el sistema queda en propuesta de autor | Constitution explicita "a titulo personal" hasta endorso (CONSTITUTION §8) |
| dIAra falla, se corrompe o cambia esquema sin aviso | Spec de Fase 1 define garantias y sustituibilidad de proveedor |
| SICOP/Hacienda no expone APIs ni acepta oraculos | Validar antes de spec de Fase 2; replantear scope si imposible |
| Falso positivo en alerta daña a contratista | Protocolo de rectificacion obligatorio (Fase 2 pre-requisito) |
| Sin partner bancario en 18 meses | Fase 2.5 fallback |
| Costos Stellar/Soroban a escala | Modelar a 10K obras x N anclas/dia antes de Fase 2 mainnet |
| Cambio regulatorio en SUGEF/BCCR durante Fase 3 | Diseñar bono con clawback y devolucion de remanentes (ya en CONSTITUTION §6) |

## Cronograma indicativo

Sin compromisos de fecha. Estimaciones razonables asumiendo 1 desarrollador full-time:

- **Fase 1**: spec + implementacion + testnet 90 dias = 4-6 meses.
- **Fase 2**: spec + factibilidad oraculos + implementacion + protocolo rectificacion = 6-9 meses.
- **Fase 3**: negociacion partner + regulatorio + implementacion = 12-24 meses.

Total ruta ideal: 22-39 meses desde primer commit. Con fallback Fase 2.5: agregar 6-9 meses si Fase 3 se atrasa.

---

**Version:** 0.1 (2026-05-02)
**Mantenedor:** Master Juan Alejandro Herrera Lopez (alejandroherreracr@gmail.com), a titulo personal.
