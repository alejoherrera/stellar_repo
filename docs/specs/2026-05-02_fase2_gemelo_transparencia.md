# [Fase 2] Gemelo de transparencia con alertas Soroban

## Cumplimiento constitucional

Esta spec implementa la Fase 2 declarada en `CONSTITUTION.md` §10. Cumplimientos especificos:

- **§1 Stack:** Stellar mainnet con Soroban (Rust + WASM); backend FastAPI; Cloud Run en `nifty-province-474317-m0`; Cloud SQL `mivisor-db`; Secret Manager para credenciales.
- **§2 Arquitectura:** la IA sigue siendo insumo, no autoridad; los smart contracts emiten alertas como **señal**, no gatillan acciones procedimentales; el gemelo espeja eventos, no reemplaza Hacienda/Tesoreria.
- **§3 Datos y seguridad:** datos personales (cedulas de funcionarios, contratistas) jamás on-chain en claro; solo hashes referenciales. KYC SEP-12 no aplica aun (no hay flujo de fondos en Fase 2).
- **§4 Calidad:** spec aprobada antes de código; contrato API con SICOP/Hacienda definido antes de empezar; tests Soroban con cobertura >= 80%; reconciliacion diaria automatizada.
- **§5 Roles:** servicio actua como "Validador IA" + nuevo rol "Oraculo SICOP" + nuevo rol "Oraculo Hacienda".
- **§6 Reglas de negocio:** las alertas referencian la cadena completa de hashes (evidencia + autorización + pago) en cumplimiento de "trazabilidad obligatoria".
- **§10 Fase 2:** **sin dinero on-chain**; **protocolo de rectificacion legal aprobado antes del primer despliegue**; primer destinatario de alertas a definir (recomendacion: solo CGR durante 6 meses, después evaluar publicación).

## Problema

Fase 1 resuelve la integridad de la evidencia de obra. Pero la transparencia real exige cerrar el loop con el **lado financiero**: ¿que pago corresponde a esta obra? ¿hubo autorización previa? ¿quedo evidencia técnica antes del desembolso? Sin eso, el ciudadano ve fotos verificadas pero no sabe si los pagos guardan correspondencia.

Además, la cadena de Fase 1 es un archivo pasivo: nadie es alertado cuando hay inconsistencias. Para que el sistema valga como mecanismo de control, debe **emitir señales** ante anomalías.

## Solución propuesta

Extender anchor-service con dos componentes nuevos y una capa de smart contracts:

1. **oracle-sicop**: ingesta eventos de SICOP (adjudicaciones, ordenes de compra, autorizaciones de pago) y los ancla on-chain con `manageData` y referencia al contrato. Modo dual: API si está disponible, scraping autorizado si no.
2. **oracle-hacienda**: ingesta eventos de Hacienda/Tesoreria (autorizaciones de desembolso, pagos efectuados) y los ancla on-chain. Probable acceso via convenio o consumo de portales abiertos.
3. **alert-contracts** (Soroban, Rust): contratos consultivos que evaluan reglas sobre los datos anclados (Fase 1 + oraculos) y emiten eventos públicos `AlertEmitted` cuando detectan inconsistencias. **No bloquean nada.**
4. **rectifier**: servicio que recibe rectificaciones (humano firmado) y emite eventos `AlertRetracted` o `AlertConfirmed`. Cumple el protocolo de rectificacion legal.
5. **dashboard público**: visualiza por obra la cadena completa contrato -> hito -> evidencia dIAra -> autorización de pago -> desembolso, mas cualquier alerta activa.

### Tipos de inconsistencia detectables (set inicial; ampliable por enmienda)

| Tipo | Regla | Severidad |
|------|-------|-----------|
| Pago sin evidencia | Autorización de pago en `t` sin output dIAra correspondiente al hito en `t-30d` | Alta |
| Hito sin respaldo | Hito marcado completo en SICOP sin hashes de evidencia anclados | Alta |
| Atraso de cronograma | Avance según dIAra < N% del plan en `t` | Media |
| Anomalía de monto | Pago > monto del hito | Alta |
| Obra inactiva con pago | personal+equipo = 0 por > N días y pago autorizado en ese periodo | Alta |
| Esquema dIAra invalidado | Output marcado `invalidated_by_source=true` con pago ya autorizado sobre ese output | Critica |

### Protocolo de rectificacion (pre-requisito)

Antes del primer despliegue:

1. Toda alerta tiene `state in {emitted, retracted, confirmed}`.
2. Una alerta nace en `emitted` y solo es pública para CGR durante una **ventana de moderacion** (recomendado 5 días habiles).
3. CGR (o el destinatario primario) puede emitir `retract(alert_id, reason)` firmado, lo que cambia state a `retracted` y pública una contra-alerta.
4. Si la ventana cierra sin retraccion, la alerta pasa a `confirmed` y se pública via dashboard público.
5. **Fuera de la cadena**: documento legal firmado entre autor del repo y CGR que define responsabilidad por difamacion de falsos positivos. Sin ese documento, no hay despliegue.

### Decisiones criticas (deben cerrarse en revision de spec)

1. **¿SICOP tiene API consumible?** Si no, ¿es legal el scraping autorizado por la institucion duena de SICOP?
2. **¿Hacienda expone eventos de desembolso?** Si no, ¿se puede establecer convenio para acceso programatico?
3. **Granularidad de alertas:** una por inconsistencia (verbosidad) vs agregadas semanalmente (perdida de inmediatez).
4. **Reglas configurables:** los umbrales (N días, N%) son por proyecto o globales.
5. **Rotacion de llaves de oraculos:** frecuencia y custodia.

## Archivos afectados

Nuevos:

```
oracle-sicop/                    # similar estructura a anchor-service
oracle-hacienda/                 # similar estructura a anchor-service
alert-contracts/                 # contratos Soroban
├── Cargo.toml
├── src/
│   ├── lib.rs
│   ├── rules/
│   │   ├── pago_sin_evidencia.rs
│   │   ├── hito_sin_respaldo.rs
│   │   ├── atraso_cronograma.rs
│   │   ├── anomalia_monto.rs
│   │   ├── obra_inactiva_pago.rs
│   │   └── esquema_invalidado.rs
│   └── events.rs
└── tests/
rectifier/                       # servicio de rectificacion
dashboard/                       # frontend público (Next.js o equivalente)
```

Modificados:

- `anchor-service`: agregar endpoints para que oraculos consulten outputs por obra/fecha.
- DB schema `anchor`: nuevas tablas `pago`, `autorización`, `hito_contrato`, `alerta`, `rectificacion`.

## Criterios de aceptacion

### Funcionales

1. Una autorización de pago en SICOP queda anclada on-chain dentro de las 24h.
2. Un desembolso en Hacienda queda anclado on-chain dentro de las 24h.
3. Una inconsistencia detectada por reglas dispara `AlertEmitted` on-chain dentro de 1h.
4. Una alerta entra a moderacion privada para CGR; tras la ventana sin retraccion, se pública.
5. Una `retract` firmada por CGR genera evento `AlertRetracted` on-chain.
6. El dashboard público muestra por obra la cadena completa de hashes y alertas activas.
7. Si un output dIAra es invalidado retroactivamente y existia pago autorizado sobre el, se emite alerta `Critica`.

### No funcionales

- Latencia evento SICOP/Hacienda -> ancla < 6h p95.
- Latencia inconsistencia detectada -> AlertEmitted < 1h p95.
- Cobertura tests Soroban >= 80% de paths.
- 0 falsos positivos en testnet durante 60 días antes de mainnet.

### Criterios de despliegue mainnet

1. Factibilidad de SICOP y Hacienda confirmada (ambos oraculos funcionando en testnet con datos reales).
2. Protocolo de rectificacion firmado entre autor y CGR.
3. 60 días en testnet con 0 falsos positivos.
4. Dashboard público revisado por al menos un asesor legal.
5. Sign-off del autor.

## Riesgos

| Riesgo | Mitigacion |
|--------|------------|
| SICOP/Hacienda inaccesibles | Validar antes de spec final; replantear scope si imposible |
| Falso positivo daña a contratista | Protocolo de rectificacion + ventana de moderacion + asesoria legal |
| Costos Soroban a escala | Modelar 10K obras x N alertas/día antes de mainnet |
| Reglas demasiado sensibles (ruido) o poco sensibles (utiles solo en escandalos) | Calibracion empirica en testnet; thresholds configurables por obra |
| Dashboard público se vuelve target de litigio | Asesoria legal previa; disclaimers explicitos sobre estado de alertas |

## Tipo

Feature grande (sub-sistema completo, smart contracts nuevos, integración con dos sistemas externos institucionales, frontend público).

---

**Estado:** Borrador para revision.
**Autor:** Master Juan Alejandro Herrera Lopez, a titulo personal.
**Fecha:** 2026-05-02.
**Constitution versión requerida:** >= 0.2.
**Pre-requisito:** Fase 1 desplegada en mainnet con criterios de exito cumplidos.
