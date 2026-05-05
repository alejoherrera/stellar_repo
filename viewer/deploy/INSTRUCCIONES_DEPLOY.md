# Deploy del viewer a `${PA_DOMAIN}/stellar` (PythonAnywhere)

Configuración leída desde `scripts/.env` (gitignored). Schema en `scripts/.env.example`.

Variables requeridas:
- `PA_USER` — username de PythonAnywhere
- `PA_DOMAIN` — dominio del webapp (ej. `www.your-domain.com`)
- `PA_PROJECT_PATH` — path absoluto del Flask app en PA (ej. `/home/<USER>/<PROJECT>`)
- `GCP_PROJECT` — proyecto GCP que tiene el secret `pythonanywhere-token`

## Archivos a subir

`viewer/index.html` y los demás `viewer/deploy/stellar*.html` se suben tal cual, sin requerir edición. Todo el código JS del viewer hace fetch hacia URLs externas (Horizon + gateway IPFS), así que funciona en cualquier dominio sobre HTTPS.

## Modo automatizado (recomendado)

```bash
python scripts/deploy_to_obrapublica.py
```

Sube todos los assets, parchea `app.py` con las rutas faltantes (`/stellar`, `/stellar/dev`, `/stellar/dashboard`, `/stellar/timelapse`), recarga el webapp y verifica HTTP 200.

## Modo manual (si querés hacerlo via UI de PythonAnywhere)

### 1. Subir el HTML como template Flask

1. PA → **Files** → navegar a `${PA_PROJECT_PATH}/templates/`
2. **Upload a file** → seleccionar `viewer/deploy/stellar.html` de este repo
3. Renombrar el archivo subido a **`stellar.html`** si hace falta

### 2. Agregar la ruta en `app.py`

1. PA → **Files** → abrir `${PA_PROJECT_PATH}/app.py`
2. Asegurar que `render_template` esté importado:
   ```python
   from flask import Flask, render_template
   ```
3. Antes del bloque `if __name__ == "__main__":` (si existe), agregar:
   ```python
   @app.route("/stellar")
   def stellar():
       return render_template("stellar.html")
   ```
4. Guardar.

### 3. Recargar el web app

1. PA → tab **Web** → botón **Reload**
2. Esperar 5-10 segundos.

### 4. Verificar

Abrir `https://${PA_DOMAIN}/stellar` en el navegador. Debe mostrar el viewer con hero Spline, metadata del proyecto, lista de outputs y verificación criptográfica contra IPFS.

## Si querés cambiar de testnet a mainnet

En `viewer/index.html`, cambiar las constantes al inicio del `<script>`:
```javascript
const ACCOUNT = "<public key mainnet>";
const HORIZON = "https://horizon.stellar.org";
const EXPLORER_TX = "https://stellar.expert/explorer/public/tx/";
const EXPLORER_ACC = "https://stellar.expert/explorer/public/account/";
```
Re-deploy con `python scripts/deploy_to_obrapublica.py`.
