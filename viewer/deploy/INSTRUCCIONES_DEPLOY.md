# Deploy del viewer a obrapublica.info/stellar (PythonAnywhere)

Cuenta PA: **`alejocr`**
Server path: `/home/alejocr/diara/`

## Archivo a subir

`viewer/index.html` (de este repo) — se sube tal cual, no requiere edicion. Todo lo que hace el viewer es fetch hacia URLs externas (Horizon + gateway IPFS), así que funciona en cualquier dominio sobre HTTPS.

## Pasos (UI de PythonAnywhere)

### 1. Subir el HTML como template Flask

1. PA -> **Files** -> navegar a `/home/alejocr/diara/templates/`
2. **Upload a file** -> seleccionar `viewer/index.html` de este repo
3. Renombrar el archivo subido a **`stellar.html`**

### 2. Agregar la ruta en `app.py`

1. PA -> **Files** -> abrir `/home/alejocr/diara/app.py`
2. Localizar el bloque de imports (al inicio del archivo); asegurar que `render_template` este importado:
   ```python
   from flask import Flask, render_template
   ```
   Si ya existe la importacion (probablemente si, dado que `/ciudadanía` la usa), no hace falta tocar.
3. Al final del archivo (antes del bloque `if __name__ == "__main__":` si existe), agregar:
   ```python
   @app.route("/stellar")
   def stellar():
       return render_template("stellar.html")
   ```
4. Guardar.

### 3. Recargar el web app

1. PA -> tab **Web** -> boton verde **Reload**
2. Esperar 5-10 segundos.

### 4. Verificar

Abrir https://www.obrapublica.info/stellar en el navegador. Debe:

- Mostrar el header con la cuenta Stellar testnet y link al explorer.
- Cargar la metadata del proyecto `circunvalacion-cr` (Monitoreo ciudadano Circunvalacion San Jose, partner LanammeUCR).
- Listar 6 outputs ordenados por fecha descendente, cada uno con:
  - Imagen cargada desde IPFS gateway.
  - Tabla de metadatos (workers, machinery, phase).
  - Verificación criptográfica en verde para JSON e imagen.
  - Links a TX en stellar.expert + JSON e imagen pineados.

Si la verificación falla con error de CORS o gateway: probar abriendo la consola del navegador (F12) para ver el detalle. Pinata gateway puede tener latencia ocasional; un refresh suele resolverlo.

## Si en el futuro reanchorás mas outputs

El viewer se actualiza solo: lee la cuenta entera de Horizon. Cada vez que el `anchor_demo.py` agregue mas outputs en testnet (o en mainnet con cambio de constante `HORIZON`), aparecen automáticamente al refrescar el viewer.

## Si querés cambiar de testnet a mainnet

En `stellar.html`, cambiar las tres constantes al inicio del `<script>`:
```javascript
const ACCOUNT = "<public key mainnet>";
const HORIZON = "https://horizon.stellar.org";
const EXPLORER_TX = "https://stellar.expert/explorer/public/tx/";
const EXPLORER_ACC = "https://stellar.expert/explorer/public/account/";
```
Subir el archivo de nuevo y reload del web app.

## Alternativa: ruta /stellar/ con trailing slash

Algunos prefieren URLs con slash final. Si querés `/stellar/` en vez de `/stellar`, registrar la ruta como:
```python
@app.route("/stellar/")
def stellar():
    return render_template("stellar.html")
```
Flask redirige `/stellar` -> `/stellar/` automáticamente.
