"""Revierte los overshoots del primer fix_tildes:
- "propuestá", "ingestá", "respuestá", "cuestá" no son palabras espanolas;
  el script anterior los rompio al reemplazar "esta " sin word-boundary.
- "está {sustantivo demostrativo femenino}" debe ser "esta {sustantivo}"
  cuando es articulo demostrativo (this), no verbo (is)."""
from pathlib import Path
import re

REPO = Path(__file__).resolve().parent.parent

# Palabras compuestas rotas: revertir directamente.
COMPOUND_FIXES = {
    "propuestá": "propuesta",
    "ingestá": "ingesta",
    "respuestá": "respuesta",
    "cuestá": "cuesta",
    "encuestá": "encuesta",
    "molestán": "molestan",
    "celestá": "celesta",
}

# Demonstratives: "está {noun}" donde el noun es femenino y la frase es "this {noun}"
# (no el verbo "is").  Lista cuidada para esta base de codigo.
DEMONSTRATIVE_NOUNS = [
    "Constitución", "Constitucion",
    "página", "pagina",
    "fase", "fases",
    "obra", "obras",
    "etapa", "etapas",
    "data",
    "cuenta",
    "exploración", "exploracion",
    "semana", "semanas",
    "vez",
    "mañana", "manana",
    "tarde",
    "noche",
    "época", "epoca",
    "version", "versión",
    "iteración", "iteracion",
    "linea", "línea",
    "carpeta", "lista",
    "spec",
    "propuesta",  # "esta propuesta"
    "investigación", "investigacion",
    "publicación", "publicacion",
    "documentación", "documentacion",
    "informacion", "información",
    "metodologia", "metodología",
    "propuesta",
    "data",
    "API", "URL", "URLs",
    "tabla",
    "section", "sección", "seccion",
    "decisión", "decision",
    "regla", "reglas",
    "key", "clave",
]


def fix(text: str, stats: dict) -> str:
    # 1) Compound word fixes (substring, no word boundary needed since these aren't Spanish)
    for old, new in COMPOUND_FIXES.items():
        new_text, count = re.subn(re.escape(old), new, text)
        if count:
            stats[old] = stats.get(old, 0) + count
            text = new_text

    # 2) "está {demonstrative_noun}" -> "esta {noun}"
    for noun in DEMONSTRATIVE_NOUNS:
        # Lowercase: "está noun" -> "esta noun"
        pattern = r"\bestá " + re.escape(noun) + r"\b"
        new_text, count = re.subn(pattern, "esta " + noun, text)
        if count:
            stats[f"está {noun}"] = stats.get(f"está {noun}", 0) + count
            text = new_text
        # Title-case: "Está Noun" -> "Esta Noun"
        pattern = r"\bEstá " + re.escape(noun) + r"\b"
        new_text, count = re.subn(pattern, "Esta " + noun, text)
        if count:
            stats[f"Está {noun}"] = stats.get(f"Está {noun}", 0) + count
            text = new_text

    return text


def main():
    targets = []
    for ext in ("*.md", "*.html"):
        targets.extend(REPO.rglob(ext))
    EXCLUDE_DIRS = {".git", "node_modules", "build", "dist", "__pycache__", ".venv", "venv"}
    targets = [t for t in targets if not any(part in EXCLUDE_DIRS for part in t.parts)]

    files_changed = 0
    grand: dict = {}
    for path in targets:
        text = path.read_text(encoding="utf-8")
        local: dict = {}
        new_text = fix(text, local)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            files_changed += 1
            print(f"  [{sum(local.values()):3d}]  {path.relative_to(REPO)}")
            for k, v in local.items():
                grand[k] = grand.get(k, 0) + v

    print()
    print(f"Files changed: {files_changed}")
    print(f"Total reverts: {sum(grand.values())}")
    for k, v in sorted(grand.items(), key=lambda x: -x[1])[:30]:
        print(f"  {v:3d} x  {k!r}")


if __name__ == "__main__":
    main()
