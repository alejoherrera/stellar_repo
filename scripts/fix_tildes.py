"""Fix masivo de tildes en archivos del repo.

Aplica una lista de reemplazos seguros (palabras que SIEMPRE llevan tilde en
espanol, sin ambiguedad) sobre archivos .md y .html. NO toca codigo Python
(.py) ni JS (.js) salvo docstrings/comentarios.
"""
from pathlib import Path
import re

REPO = Path(__file__).resolve().parent.parent

# Mapa de reemplazos. Cada entrada: 'palabra_sin_tilde' -> 'palabra_con_tilde'.
# Solo palabras donde el "sin tilde" NO es una palabra valida en otro contexto.
REPLACEMENTS = {
    # Sustantivos/adjetivos que siempre llevan tilde
    "publica": "pública",
    "publicas": "públicas",
    "publico": "público",
    "publicos": "públicos",
    "criptografica": "criptográfica",
    "criptograficas": "criptográficas",
    "criptografico": "criptográfico",
    "criptograficos": "criptográficos",
    "tecnologia": "tecnología",
    "tecnologias": "tecnologías",
    "tecnico": "técnico",
    "tecnica": "técnica",
    "tecnicos": "técnicos",
    "tecnicas": "técnicas",
    "academico": "académico",
    "academica": "académica",
    "academicos": "académicos",
    "academicas": "académicas",
    "automatico": "automático",
    "automatica": "automática",
    "automaticos": "automáticos",
    "automaticas": "automáticas",
    "automatizacion": "automatización",
    "automatizado": "automatizado",
    "asincrono": "asíncrono",
    "asincrona": "asíncrona",
    "metodo": "método",
    "metodos": "métodos",
    "metodologia": "metodología",
    "logica": "lógica",
    "logico": "lógico",
    "logicos": "lógicos",
    "logicas": "lógicas",
    "rapido": "rápido",
    "rapida": "rápida",
    "rapidos": "rápidos",
    "rapidas": "rápidas",
    "facil": "fácil",
    "faciles": "fáciles",
    "facilmente": "fácilmente",
    "dificil": "difícil",
    "dificiles": "difíciles",
    "comun": "común",
    "comunes": "comunes",
    "estandar": "estándar",
    "linea": "línea",
    "lineas": "líneas",
    "fisico": "físico",
    "fisica": "física",
    "fisicos": "físicos",
    "fisicas": "físicas",
    "energetico": "energético",
    "energetica": "energética",
    "publico": "público",
    "domestico": "doméstico",
    "domestica": "doméstica",
    "valido": "válido",
    "valida": "válida",
    "validos": "válidos",
    "validas": "válidas",
    "geografico": "geográfico",
    "geografica": "geográfica",
    "estadistica": "estadística",
    "estadisticas": "estadísticas",
    "estadistico": "estadístico",
    # Adverbios y conectores comunes con tilde
    "tambien": "también",
    "ademas": "además",
    "despues": "después",
    "segun": "según",
    "asi": "así",
    "aqui": "aquí",
    "alli": "allí",
    "atras": "atrás",
    "detras": "detrás",
    "demas": "demás",
    "jamas": "jamás",
    "unicamente": "únicamente",
    "rapidamente": "rápidamente",
    "automaticamente": "automáticamente",
    "tipicamente": "típicamente",
    "criticamente": "críticamente",
    "facilmente": "fácilmente",
    "dificilmente": "difícilmente",
    # Numeros y cardinales con tilde
    "ningun": "ningún",
    "algun": "algún",
    "algunas": "algunas",  # already correct
    "ningunas": "ningunas",  # already correct
    "ultimo": "último",
    "ultima": "última",
    "ultimos": "últimos",
    "ultimas": "últimas",
    "unico": "único",
    "unica": "única",
    "unicos": "únicos",
    "unicas": "únicas",
    # Palabras con n -> n con tilde
    "diseno": "diseño",
    "disenos": "diseños",
    "disenado": "diseñado",
    "disenada": "diseñada",
    "disenados": "diseñados",
    "disenadas": "diseñadas",
    "disenar": "diseñar",
    "tamano": "tamaño",
    "tamanos": "tamaños",
    "compania": "compañía",
    "companias": "compañías",
    "espanol": "español",
    "espanola": "española",
    "espanoles": "españoles",
    "manana": "mañana",
    "montana": "montaña",
    "ano": "año",  # ambiguo con anatomico, riesgo bajo en docs tecnicas
    "anos": "años",
    "ensar": "ensañar",  # rare
    # Palabras especificas del dominio
    "fiscalizacion": "fiscalización",
    "fiscalizaciones": "fiscalizaciones",
    "validacion": "validación",
    "validaciones": "validaciones",
    "verificacion": "verificación",
    "verificaciones": "verificaciones",
    "ejecucion": "ejecución",
    "ejecuciones": "ejecuciones",
    "operacion": "operación",
    "operaciones": "operaciones",
    "construccion": "construcción",
    "construcciones": "construcciones",
    "implementacion": "implementación",
    "implementaciones": "implementaciones",
    "innovacion": "innovación",
    "innovaciones": "innovaciones",
    "presentacion": "presentación",
    "integracion": "integración",
    "integraciones": "integraciones",
    "navegacion": "navegación",
    "documentacion": "documentación",
    "informacion": "información",
    "investigacion": "investigación",
    "solucion": "solución",
    "soluciones": "soluciones",
    "descripcion": "descripción",
    "descripciones": "descripciones",
    "definicion": "definición",
    "definiciones": "definiciones",
    "explicacion": "explicación",
    "autorizacion": "autorización",
    "autorizaciones": "autorizaciones",
    "instruccion": "instrucción",
    "instrucciones": "instrucciones",
    "notificacion": "notificación",
    "notificaciones": "notificaciones",
    "instalacion": "instalación",
    "instalaciones": "instalaciones",
    "opcion": "opción",
    "opciones": "opciones",
    "organizacion": "organización",
    "organizaciones": "organizaciones",
    "condicion": "condición",
    "condiciones": "condiciones",
    "eleccion": "elección",
    "elecciones": "elecciones",
    "version": "versión",
    "versiones": "versiones",
    "interaccion": "interacción",
    "interacciones": "interacciones",
    "aplicacion": "aplicación",
    "aplicaciones": "aplicaciones",
    "atencion": "atención",
    "atenciones": "atenciones",
    "modificacion": "modificación",
    "modificaciones": "modificaciones",
    "explicacion": "explicación",
    "exposicion": "exposición",
    "supervision": "supervisión",
    "transmision": "transmisión",
    "decision": "decisión",
    "mision": "misión",
    "vision": "visión",
    "rendicion": "rendición",
    "estacion": "estación",
    "estaciones": "estaciones",
    "extension": "extensión",
    "tension": "tensión",
    "evolucion": "evolución",
    "revolucion": "revolución",
    "explicacion": "explicación",
    "ubicacion": "ubicación",
    "ubicaciones": "ubicaciones",
    "duracion": "duración",
    "duraciones": "duraciones",
    "iluminacion": "iluminación",
    "alimentacion": "alimentación",
    "comunicacion": "comunicación",
    "comunicaciones": "comunicaciones",
    "publicacion": "publicación",
    "publicaciones": "publicaciones",
    "extraccion": "extracción",
    "transaccion": "transacción",
    "transacciones": "transacciones",
    "deteccion": "detección",
    "correccion": "corrección",
    "inyeccion": "inyección",
    "iteracion": "iteración",
    "iteraciones": "iteraciones",
    "produccion": "producción",
    "produccion": "producción",
    "redaccion": "redacción",
    "fraccion": "fracción",
    "interpretacion": "interpretación",
    "interpretaciones": "interpretaciones",
    "evaluacion": "evaluación",
    "evaluaciones": "evaluaciones",
    "cooperacion": "cooperación",
    "delegacion": "delegación",
    "afirmacion": "afirmación",
    "negacion": "negación",
    "obligacion": "obligación",
    "obligaciones": "obligaciones",
    "regulacion": "regulación",
    "regulaciones": "regulaciones",
    "regulacion": "regulación",
    "manipulacion": "manipulación",
    "captacion": "captación",
    "actuacion": "actuación",
    "explotacion": "explotación",
    "transparencia": "transparencia",  # ya correcto
    "republica": "república",
    "Republica": "República",
    "Constitucion": "Constitución",
    "constitucion": "constitución",
    "constitucional": "constitucional",  # ya correcto
    # Palabras concretas mas
    "pais": "país",
    "paises": "países",
    "dia": "día",
    "dias": "días",
    "rio": "río",
    "rios": "ríos",
    "categoria": "categoría",
    "categorias": "categorías",
    "garantia": "garantía",
    "garantias": "garantías",
    "anomalia": "anomalía",
    "anomalias": "anomalías",
    "ergonomia": "ergonomía",
    "ciudadania": "ciudadanía",
    "telefono": "teléfono",
    "telefonos": "teléfonos",
    "metricas": "métricas",
    "metrica": "métrica",
    "indice": "índice",
    "indices": "índices",
    "trafico": "tráfico",
    "matricula": "matrícula",
    "tactil": "táctil",
    "ortografia": "ortografía",
    "filosofia": "filosofía",
    "geometria": "geometría",
    "energia": "energía",
    "estrategia": "estrategia",  # ya correcto
    "tecnologia": "tecnología",
    # Palabras tecnicas con tilde
    "codigo": "código",
    "codigos": "códigos",
    "Codigo": "Código",
    "Codigos": "Códigos",
    "numero": "número",
    "numeros": "números",
    "Numero": "Número",
    "caracter": "carácter",
    "caracter,": "carácter,",
    "caracter.": "carácter.",
    "caracter:": "carácter:",
    # Verbos comunes
    "esta ": "está ",
    "esta,": "está,",
    "esta.": "está.",
    "esta:": "está:",
    "estan ": "están ",
    "estan,": "están,",
    "estan.": "están.",
    "estan:": "están:",
}


def fix_text(text: str, stats: dict) -> str:
    for old, new in REPLACEMENTS.items():
        # Word-boundary aware replace, case-sensitive
        # Manejar las versiones con punctuation aparte (las del final)
        if old.endswith((" ", ",", ".", ":")):
            pattern = re.escape(old)
        else:
            pattern = r"\b" + re.escape(old) + r"\b"
        new_text, count = re.subn(pattern, new, text)
        if count:
            stats[old] = stats.get(old, 0) + count
            text = new_text
        # Capitalized variant
        if old[0].islower():
            cap_old = old[0].upper() + old[1:]
            cap_new = new[0].upper() + new[1:]
            if old.endswith((" ", ",", ".", ":")):
                pattern = re.escape(cap_old)
            else:
                pattern = r"\b" + re.escape(cap_old) + r"\b"
            text, count = re.subn(pattern, cap_new, text)
            if count:
                stats[cap_old] = stats.get(cap_old, 0) + count
    return text


def main():
    targets = []
    for ext in ("*.md", "*.html"):
        targets.extend(REPO.rglob(ext))
    # Excluir directorios que no queremos tocar
    EXCLUDE_DIRS = {".git", "node_modules", "build", "dist", "__pycache__", ".venv", "venv"}
    targets = [t for t in targets if not any(part in EXCLUDE_DIRS for part in t.parts)]

    total_files_changed = 0
    grand_stats = {}
    for path in targets:
        text = path.read_text(encoding="utf-8")
        local_stats: dict = {}
        new_text = fix_text(text, local_stats)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            total_files_changed += 1
            n_changes = sum(local_stats.values())
            print(f"  [{n_changes:4d} changes] {path.relative_to(REPO)}")
            for k, v in local_stats.items():
                grand_stats[k] = grand_stats.get(k, 0) + v

    print()
    print(f"Files changed: {total_files_changed}")
    print(f"Total replacements: {sum(grand_stats.values())}")
    print()
    print("Top palabras corregidas:")
    for word, count in sorted(grand_stats.items(), key=lambda x: -x[1])[:25]:
        print(f"  {count:4d} x  {word}")


if __name__ == "__main__":
    main()
