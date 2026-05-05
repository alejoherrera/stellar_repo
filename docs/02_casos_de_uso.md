# 02 — Casos de uso

Cinco casos de uso identificados, ordenados de menor a mayor ambicion. No son alternativos: son **capas que se acumulan**. La Fase 1 (anclaje en Stellar) implementa caso A. La Fase 2 (gemelo de transparencia) suma B y C. La Fase 3 (bono tokenizado) los combina todos via D y E. Ver `09_roadmap_etapas.md` y `CONSTITUTION.md §10` para la hoja de fases vigente.

---

## Caso A — Notarizacion del output de IA sobre avance de obra

**Que:** anclar en Stellar el hash de cada reporte generado por un modelo de IA que evalua el avance físico de una obra pública, junto con metadatos minimos: hash del modelo, versión del prompt, hash de la evidencia (foto, BIM, video), timestamp.

**Por que:** convierte el output de la IA en evidencia con timestamp inmutable. Si mañana se demuestra que el modelo se equivoco o estaba sesgado, queda traza historica. Si el contratista o la institucion intentan después "reescribir" lo que la IA dijo, no pueden.

**Lo que prueba:** *que* se dijo, *cuando* y *quien firmo*. **No** prueba que sea cierto.

**Costo on-chain:** una transacción Stellar con `manageData` o un evento Soroban por reporte. Centavos.

**Fuera de alcance:** validación de la veracidad del reporte (eso lo agrega el caso B).

---

## Caso B — Validación ciudadana en capas

**Que:** cuatro capas de participacion ciudadana, desde la pasiva hasta la activa.

| Capa | Accion ciudadana | Requiere wallet |
|------|------------------|-----------------|
| 1. Verificación pasiva | Lee viewer público, calcula hash y verifica integridad del reporte | No |
| 2. Observacion de realidad | Sube foto geolocalizada de la obra, comparada contra reporte oficial | Si (custodial) |
| 3. Disputa formal | Inicia disputa on-chain referenciando hash del reporte | Si (custodial o propia) |
| 4. Reputacion del modelo | Lectura agregada del track record de la IA y de los inspectores | No |

**Por que:** el blockchain prueba inmutabilidad, no veracidad. La validación ciudadana convierte la inmutabilidad en accountability real.

**Limitaciones honestas:** liveness de fotos, GPS spoofing, sybil attacks, friccion de wallet. Doc detallado de validación ciudadana queda como pendiente.

**Dependencias:** caso A (sin reportes anclados, no hay nada que validar).

---

## Caso C — Gemelo on-chain del flujo de pagos públicos

**Que:** mantener un espejo en blockchain de cada evento financiero relevante de la obra pública. **No mueve dinero on-chain.** El sistema bancario tradicional (Tesoreria → SINPE → contratista) sigue siendo la autoridad legal y única fuente de movimiento real de valor. La cadena espeja eventos:

- Adjudicacion del contrato (hash del cartel + monto + cronograma + wallets autorizadas)
- Cada autorización de pago (monto, justificacion, hash del reporte IA, firmas)
- Cada confirmacion de desembolso real (referencia SINPE, monto efectivo, fecha)
- Cierre y liquidacion (remanentes, garantías)

**Por que:** transparencia pública sin tocar Hacienda. Cero friccion legal porque no es medio de pago, es publicación de información (encaja con articulo 11 constitucional y Ley 7428).

**Limitaciones honestas:** garbage in / garbage out. Si el oraculo que ancla la confirmacion SINPE miente, la cadena refleja la mentira con timestamp inmutable. Mitigacion: idealmente el evento de confirmacion lo emite el propio sistema de Tesoreria (oraculo autoritativo); reconciliacion periodica contra datos oficiales (SICOP, presupuesto público).

**Dependencias:** casos A y B son insumos del gemelo.

**Está es la base de la Fase 2 del roadmap actual.** Politicamente factible hoy, sin reforma legal. (Nota: en una iteración anterior del roadmap este caso era Etapa 1; el modelo vigente lo posiciona como Fase 2 con dIAra como Fase 0 externa y Fase 1 = anclaje minimo.)

---

## Caso D — Presupuesto programable / escrow con liberacion por hitos

**Que:** los fondos de la obra (en USDC u otro stablecoin) se depositan en un contrato Soroban. El contrato libera tranches a la wallet del contratista solo cuando se cumplen condiciones definidas:

- Hito de cronograma alcanzado
- Reporte IA con score >= umbral
- Firma de inspector + auditor (M-de-N, M >= 2)
- Ventana de veto ciudadano vencida sin disputa abierta

Penalidades por atraso, devolucion de remanentes y reasignacion en caso de incumplimiento, todo automatizado.

**Por que:** elimina la posibilidad de pagos "discrecionales" sin justificacion. El dinero solo se mueve si la cadena de evidencia está completa.

**Limitaciones legales en CR:** Ley de Contratacion Administrativa probablemente no permite hoy que un contrato inteligente sea el medio de pago oficial. Por eso esta etapa requiere o (a) piloto financiado por cooperación internacional (BID, Banco Mundial, BCIE) que opera fuera del flujo legal doméstico, o (b) reforma o reglamentacion especifica.

**Limitaciones técnicas:** custodia de la llave maestra del escrow. Riesgo enorme si se compromete. Exige multisig hardware + procedimientos institucionales serios.

**Dependencias:** casos A, B y C.

---

## Caso E — Bono tokenizado emitido por banco de desarrollo

**Que:** un banco de desarrollo (idealmente BCIE; alternativas: Banco Popular, IFAM, SBD) emite un bono cuyo capital financia la obra pública. El bono está tokenizado en Stellar:

- Cada token = fracción de la deuda
- Inversionistas (institucionales o retail acreditado) compran tokens, capital ingresa al escrow del caso D
- Cupones se distribuyen on-chain a los holders proporcionalmente
- Al vencimiento, principal devuelto

**Por que:** combina financiamiento + transparencia + escrow programable en un instrumento financiero único que **no existe hoy en LATAM en producción**. Atrae capital institucional internacional (apetito ESG / impacto) hacia infraestructura costarricense con auditabilidad completa.

**Variantes alternativas (analisis detallado pendiente como documento separado):**

1. Bono tokenizado puro (la que se describe arriba)
2. Stablecoin del banco de desarrollo
3. Token de desembolso condicional (D embebido en E)
4. Impact token / outcome-based
5. Hibrido bono + escrow (recomendado)

**Precedentes internacionales:**

- **Société Générale** emitio bonos en Stellar en 2024 para clientes institucionales
- **World Bank "Bond-i"** en Ethereum (2018, AUD$110M)
- **BID Lab** piloto en BNB Chain
- Bonos verdes tokenizados en Polygon

**Limitaciones regulatorias en CR:** SUGEVAL aplica. Ley 7732 podria requerir reforma o uso de figura "oferta privada / inversionistas sofisticados" para no requerir prospecto público. BCIE como emisor multilateral tiene menos friccion regulatoria doméstica.

**Dependencias:** todos los anteriores.

---

## Como se combinan en una arquitectura coherente

```
                     INVERSIONISTAS
                     (institucionales / retail acreditado)
                            │
                            │ compran bono tokenizado
                            ▼
            BANCO DE DESARROLLO (BCIE/Banco Popular/IFAM)
                  Emite asset tokenizado en Stellar
                            │
                            │ capital ingresa a escrow
                            ▼
                    SOROBAN ESCROW CONTRACT (por obra)
                  ┌──────────────────────────────┐
                  │ Hito 1: 20%                  │
                  │ Hito 2: 30%                  │
                  │ Hito 3: 30%                  │
                  │ Hito 4 (cierre): 20%         │
                  └──────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         REPORTE IA    INSPECTOR      AUDITOR
        (firma de     (firma de      (firma
         servicio)     identidad      independiente)
                       MICITT)
                            │
                            │ M-de-N firmas + ventana de veto ciudadano
                            ▼
                   LIBERACION DE TRANCHE
                            │
                            ▼
                   WALLET DEL CONTRATISTA
                            │
                            │ off-ramp via anchor (Bitso, MoneyGram, etc.)
                            ▼
                       SISTEMA BANCARIO TRADICIONAL
                       (cuenta CR del contratista)


    EN PARALELO (gemelo de transparencia):

    Cada evento (adjudicacion, autorización, desembolso real, cierre)
    se ancla on-chain con todos sus hashes y firmas.

    Viewer público permite a ciudadanos:
      - Ver el estado de cualquier obra en tiempo real
      - Verificar hashes de reportes
      - Subir observaciones de campo
      - Iniciar disputas
```

## Que se construye primero (modelo vigente)

**Fase 0 (externa):** dIAra produce datos analizados por IA + imagenes. Ya desplegado, fuera del alcance de este repo.

**Fase 1 (Caso A):** anclaje minimo en Stellar de los outputs de dIAra. Sin Soroban, sin pagos. Ya implementada en testnet (ver `specs/2026-05-02_fase1_anclaje_stellar.md`).

**Fase 2 (Caso B + Caso C):** gemelo de transparencia que extiende Fase 1 con eventos de pago de SICOP/Hacienda + alertas via Soroban. Sin dinero on-chain. Spec disponible en `specs/2026-05-02_fase2_gemelo_transparencia.md`.

**Fase 3 (Caso E, bono tokenizado):** combina todo. Requiere partner bancario, regulatorio, anchor CRC<->Stellar, custodia institucional.

**Fallback Fase 2.5 (Caso D, escrow piloto):** activable si Fase 3 no logra partner bancario en 18 meses.

Detalle en `09_roadmap_etapas.md` y normativo en `CONSTITUTION.md §10`.
