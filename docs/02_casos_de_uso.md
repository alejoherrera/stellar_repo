# 02 — Casos de uso

Cinco casos de uso identificados, ordenados de menor a mayor ambicion. No son alternativos: son **capas que se acumulan**. La Fase 1 (anclaje en Stellar) implementa caso A. La Fase 2 (gemelo de transparencia) suma B y C. La Fase 3 (bono tokenizado) los combina todos via D y E. Ver `09_roadmap_etapas.md` y `CONSTITUTION.md §10` para la hoja de fases vigente.

---

## Caso A — Notarizacion del output de IA sobre avance de obra

**Que:** anclar en Stellar el hash de cada reporte generado por un modelo de IA que evalua el avance fisico de una obra publica, junto con metadatos minimos: hash del modelo, version del prompt, hash de la evidencia (foto, BIM, video), timestamp.

**Por que:** convierte el output de la IA en evidencia con timestamp inmutable. Si manana se demuestra que el modelo se equivoco o estaba sesgado, queda traza historica. Si el contratista o la institucion intentan despues "reescribir" lo que la IA dijo, no pueden.

**Lo que prueba:** *que* se dijo, *cuando* y *quien firmo*. **No** prueba que sea cierto.

**Costo on-chain:** una transaccion Stellar con `manageData` o un evento Soroban por reporte. Centavos.

**Fuera de alcance:** validacion de la veracidad del reporte (eso lo agrega el caso B).

---

## Caso B — Validacion ciudadana en capas

**Que:** cuatro capas de participacion ciudadana, desde la pasiva hasta la activa.

| Capa | Accion ciudadana | Requiere wallet |
|------|------------------|-----------------|
| 1. Verificacion pasiva | Lee viewer publico, calcula hash y verifica integridad del reporte | No |
| 2. Observacion de realidad | Sube foto geolocalizada de la obra, comparada contra reporte oficial | Si (custodial) |
| 3. Disputa formal | Inicia disputa on-chain referenciando hash del reporte | Si (custodial o propia) |
| 4. Reputacion del modelo | Lectura agregada del track record de la IA y de los inspectores | No |

**Por que:** el blockchain prueba inmutabilidad, no veracidad. La validacion ciudadana convierte la inmutabilidad en accountability real.

**Limitaciones honestas:** liveness de fotos, GPS spoofing, sybil attacks, friccion de wallet. Doc detallado de validacion ciudadana queda como pendiente.

**Dependencias:** caso A (sin reportes anclados, no hay nada que validar).

---

## Caso C — Gemelo on-chain del flujo de pagos publicos

**Que:** mantener un espejo en blockchain de cada evento financiero relevante de la obra publica. **No mueve dinero on-chain.** El sistema bancario tradicional (Tesoreria → SINPE → contratista) sigue siendo la autoridad legal y unica fuente de movimiento real de valor. La cadena espeja eventos:

- Adjudicacion del contrato (hash del cartel + monto + cronograma + wallets autorizadas)
- Cada autorizacion de pago (monto, justificacion, hash del reporte IA, firmas)
- Cada confirmacion de desembolso real (referencia SINPE, monto efectivo, fecha)
- Cierre y liquidacion (remanentes, garantias)

**Por que:** transparencia publica sin tocar Hacienda. Cero friccion legal porque no es medio de pago, es publicacion de informacion (encaja con articulo 11 constitucional y Ley 7428).

**Limitaciones honestas:** garbage in / garbage out. Si el oraculo que ancla la confirmacion SINPE miente, la cadena refleja la mentira con timestamp inmutable. Mitigacion: idealmente el evento de confirmacion lo emite el propio sistema de Tesoreria (oraculo autoritativo); reconciliacion periodica contra datos oficiales (SICOP, presupuesto publico).

**Dependencias:** casos A y B son insumos del gemelo.

**Esta es la base de la Fase 2 del roadmap actual.** Politicamente factible hoy, sin reforma legal. (Nota: en una iteracion anterior del roadmap este caso era Etapa 1; el modelo vigente lo posiciona como Fase 2 con dIAra como Fase 0 externa y Fase 1 = anclaje minimo.)

---

## Caso D — Presupuesto programable / escrow con liberacion por hitos

**Que:** los fondos de la obra (en USDC u otro stablecoin) se depositan en un contrato Soroban. El contrato libera tranches a la wallet del contratista solo cuando se cumplen condiciones definidas:

- Hito de cronograma alcanzado
- Reporte IA con score >= umbral
- Firma de inspector + auditor (M-de-N, M >= 2)
- Ventana de veto ciudadano vencida sin disputa abierta

Penalidades por atraso, devolucion de remanentes y reasignacion en caso de incumplimiento, todo automatizado.

**Por que:** elimina la posibilidad de pagos "discrecionales" sin justificacion. El dinero solo se mueve si la cadena de evidencia esta completa.

**Limitaciones legales en CR:** Ley de Contratacion Administrativa probablemente no permite hoy que un contrato inteligente sea el medio de pago oficial. Por eso esta etapa requiere o (a) piloto financiado por cooperacion internacional (BID, Banco Mundial, BCIE) que opera fuera del flujo legal domestico, o (b) reforma o reglamentacion especifica.

**Limitaciones tecnicas:** custodia de la llave maestra del escrow. Riesgo enorme si se compromete. Exige multisig hardware + procedimientos institucionales serios.

**Dependencias:** casos A, B y C.

---

## Caso E — Bono tokenizado emitido por banco de desarrollo

**Que:** un banco de desarrollo (idealmente BCIE; alternativas: Banco Popular, IFAM, SBD) emite un bono cuyo capital financia la obra publica. El bono esta tokenizado en Stellar:

- Cada token = fraccion de la deuda
- Inversionistas (institucionales o retail acreditado) compran tokens, capital ingresa al escrow del caso D
- Cupones se distribuyen on-chain a los holders proporcionalmente
- Al vencimiento, principal devuelto

**Por que:** combina financiamiento + transparencia + escrow programable en un instrumento financiero unico que **no existe hoy en LATAM en produccion**. Atrae capital institucional internacional (apetito ESG / impacto) hacia infraestructura costarricense con auditabilidad completa.

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

**Limitaciones regulatorias en CR:** SUGEVAL aplica. Ley 7732 podria requerir reforma o uso de figura "oferta privada / inversionistas sofisticados" para no requerir prospecto publico. BCIE como emisor multilateral tiene menos friccion regulatoria domestica.

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

    Cada evento (adjudicacion, autorizacion, desembolso real, cierre)
    se ancla on-chain con todos sus hashes y firmas.

    Viewer publico permite a ciudadanos:
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
