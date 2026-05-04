# 01 — Motivacion y contexto

## El problema

La inversion publica en obra de infraestructura en Costa Rica adolece de problemas estructurales que ningun sistema de informacion tradicional ha resuelto satisfactoriamente:

1. **Opacidad operativa.** El ciudadano no puede ver, en tiempo real y de forma confiable, el estado de avance de una obra que paga con sus impuestos. La informacion esta fragmentada entre SICOP, paginas institucionales, expedientes administrativos y prensa.
2. **Auditoria episodica, no continua.** La CGR audita por muestreo y a posteriori. Cuando se detecta un problema (sobreprecios, atrasos sistematicos, pagos sin contraparte), el dano ya ocurrio.
3. **Reportes alterables.** Documentos, fechas y justificaciones pueden modificarse retroactivamente en sistemas administrativos sin que quede rastro publico inmutable.
4. **Asimetria de informacion entre Estado, contratista y ciudadania.** El contratista sabe lo que esta haciendo; el supervisor sabe lo que reporta el contratista; la institucion sabe lo que el supervisor le dice; el ciudadano se entera meses despues, si acaso.
5. **Falta de mecanismos de validacion ciudadana estructurada.** Quejas via redes sociales o medios no se integran al expediente formal. La denuncia ante CGR es de alta fricion y baja respuesta.

## Que NO se busca con este proyecto

Antes de explicar la propuesta es importante delimitar lo que **no** es, porque hay confusiones recurrentes cuando se menciona "blockchain" en contextos publicos:

- **No** sustituir el sistema bancario ni a Tesoreria Nacional.
- **No** descentralizar funciones soberanas del Estado.
- **No** crear un token especulativo ni instrumento expuesto al publico minorista sin regulacion.
- **No** depender de criptomonedas volatiles para pagar contratistas.
- **No** delegar decisiones politicas o tecnicas en un algoritmo de IA.

## Que **si** se busca

- **Capa publica de transparencia inmutable** sobre el flujo de obra publica: que es imposible ocultar, alterar o "borrar" reportes negativos despues de publicados.
- **Auditabilidad continua** que CGR, ciudadania y prensa puedan ejercer sin pedir permiso ni esperar respuesta a oficios.
- **Trazabilidad cripto-verificable** entre evidencia (foto, BIM, reporte IA), validaciones (firmas humanas), y autorizaciones de pago.
- **Reduccion de friccion** para que ciudadanos contribuyan observaciones de campo de forma estructurada y verificable.
- **Eventualmente, financiamiento programable** de obra publica via instrumentos tokenizados emitidos por banca de desarrollo, con liberacion de fondos atada a hitos validados.

## Por que Stellar

Cuatro razones tecnicas y una de oportunidad:

1. **Emision de assets es nativa.** En Stellar, emitir un token (sea bono tokenizado, stablecoin institucional o asset de prueba) es una operacion primitiva del protocolo, no requiere desplegar contratos complejos. Mas simple, mas barato, mas auditable que ERC-20.
2. **Compliance tooling maduro.** Authorization flags por cuenta (`AUTH_REQUIRED`, `AUTH_REVOCABLE`, `AUTH_CLAWBACK_ENABLED`) permiten al emisor revertir tokens por orden judicial. Casi unico entre las grandes blockchains y critico para banca regulada.
3. **Soroban (Rust + WASM) para logica.** Desde 2024 Stellar tiene smart contracts completos. Permite codificar escrow, multisig de validadores, ventanas de veto, penalidades automaticas.
4. **SEPs estandarizan integracion.** SEP-10 (auth), SEP-12 (KYC reutilizable), SEP-24 (rampa fiat), SEP-31 (pagos transfronterizos institucionales) ofrecen patrones probados para integrar entidades reguladas.
5. **Costo despreciable.** Anclar miles de eventos por mes cuesta centavos. Distribuir cupones de un bono a 10,000 holders cuesta menos que una transferencia bancaria.

**Ventaja de oportunidad:** Société Générale emitio bonos en Stellar en 2024; MoneyGram opera off-ramp a fiat en CR via Stellar; Circle emite USDC nativo en Stellar. La infraestructura regional LATAM (Bitso, Lemon, Belo) tiene anchors Stellar. Si en algun horizonte el Banco Central de Costa Rica avanza con CBDC, Stellar es uno de los rails ya probados.

## Por que **no** otra cadena (resumen)

Comparativa detallada queda como documento pendiente; en breve:

- **Hedera HCS** es ligeramente mejor para puro timestamping de mensajes ordenados. Pierde en emision de assets y en ecosistema LATAM.
- **Polygon / Ethereum L2s** son mas maduros para attestations (EAS) pero costos variables y ecosistema mas orientado a DeFi que a banca regulada.
- **Algorand** tiene buen track record en sector publico (Italia, Marshall Islands) y assets nativos como Stellar; pierde en presencia regional y en partnerships bancarios.
- **Arweave** es excelente si se quiere que el reporte completo viva on-chain para siempre, pero no resuelve la dimension de logica programable ni de assets.

Ninguna decision esta cerrada — la Constitucion fija Stellar como stack inicial, pero una enmienda formal podria cambiarla si la evidencia lo justifica antes de pasar a codigo.

## Contexto institucional Costa Rica

- **Articulo 11 constitucional:** principios de publicidad, transparencia y rendicion de cuentas. Base legal robusta para publicar informacion de obra publica de forma proactiva.
- **Ley 7428 (Organica de la CGR):** fortalece auditabilidad continua. Compatible con un gemelo on-chain como capa adicional de evidencia.
- **Ley 7732 (Mercado de Valores):** marco para eventual emision de bono tokenizado. Requiere SUGEVAL en el bucle.
- **Acuerdo SUGEF 12-21:** regula proveedores de servicios de activos virtuales. Aplica si se opera anchor o exchange.
- **Firma digital MICITT:** infraestructura de identidad ya operativa. Puede mapearse a llaves Stellar via DID, sin reinventar identidad.

## Stakeholders potenciales

| Stakeholder | Rol potencial | Modo de involucramiento sugerido |
|-------------|---------------|----------------------------------|
| **CGR** | Observador privilegiado, validador externo | Alineamiento con su mandato de fiscalizacion |
| **BCIE** | Emisor de bono tokenizado, financiador piloto | Interlocucion con comite tecnico |
| **BCCR** | Eventual emisor de CBDC compatible | Exploratoria, horizonte largo |
| **SUGEVAL** | Regulador del bono | Acompanamiento regulatorio formal |
| **SUGEF** | Regulador de activos virtuales / KYC | Acuerdo SUGEF 12-21 como base |
| **MOPT, municipalidades** | Usuarios primarios del sistema | Piloto institucional con caso concreto |
| **Banco Popular, IFAM** | Alternativas domesticas a BCIE | Interlocucion con area de innovacion |
| **Cooperacion internacional (BID, BM)** | Financiador piloto inicial | Alineamiento con agenda de innovacion publica |
| **Universidades (UCR, TEC, UNED)** | Validacion academica, investigacion | Convenio de investigacion conjunta |
| **Estado de la Nacion / Costa Rica Integra** | Aliados sociedad civil | Alianza temprana, alineamiento de mision |

## Origen de esta exploracion

Esta linea de trabajo nace de una conversacion entre el responsable tecnico y el asistente de IA el 2026-04-29, en el marco de exploracion de aplicaciones de Stellar mas alla de pagos. La conversacion progreso en cinco saltos sucesivos:

1. ¿Stellar sirve para algo distinto a transacciones bancarias?
2. ¿Y si registramos publicamente el output de IA sobre avance de obra?
3. ¿Que podria validar el ciudadano?
4. ¿Y si tokenizamos el presupuesto de la obra y lo atamos al monitoreo?
5. ¿Y si proponemos un token para banco de desarrollo en emprestitos de obra?

Cada salto es una capa adicional de la misma arquitectura. Este repo organiza esas capas en una propuesta coherente.
