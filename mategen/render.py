"""Salida del examen en Markdown, texto plano y HTML.

El HTML se arma con un conversor de Markdown mínimo escrito acá mismo: el
programa no depende de ninguna biblioteca externa, así que corre en cualquier
computadora con Python 3 instalado y sin conexión.
"""

import html as _html
import re
from datetime import date
from typing import Dict, List

from .ejercicio import Ejercicio


# ==========================================================================
# Markdown
# ==========================================================================

def a_markdown(examen: Dict, con_soluciones: bool = True, soluciones_aparte: bool = False) -> str:
    partes: List[str] = []
    ejercicios: List[Ejercicio] = examen["ejercicios"]

    partes.append(f"# {examen['titulo']} — Matemática I")
    partes.append(
        f"*Tecnicatura/Licenciatura en Informática — generado el "
        f"{date.today().strftime('%d/%m/%Y')}*\n\n"
        f"**Semilla:** `{examen['semilla']}` (con la misma semilla se obtiene el mismo "
        f"examen) · **Puntaje total:** {examen['puntaje_total']} puntos · "
        f"**Aprobación:** 60 puntos"
    )
    partes.append(
        "> Justificar todas las respuestas: una respuesta sin justificación no se "
        "considera correcta."
    )
    partes.append("\n---\n")

    for i, ej in enumerate(ejercicios, start=1):
        partes.append(f"## Ejercicio {i} — {ej.tema}: {ej.subtema}  *({ej.puntaje} pts)*")
        partes.append(ej.consigna)
        if con_soluciones and not soluciones_aparte:
            partes.append(_resolucion_markdown(ej))
        partes.append("\n---\n")

    if con_soluciones and soluciones_aparte:
        partes.append("# Resoluciones\n")
        for i, ej in enumerate(ejercicios, start=1):
            partes.append(f"## Resolución del Ejercicio {i} — {ej.subtema}")
            partes.append(_resolucion_markdown(ej))
            partes.append("\n---\n")

    return "\n\n".join(partes)


def _resolucion_markdown(ej: Ejercicio) -> str:
    bloques = ["### Resolución"]
    for j, paso in enumerate(ej.pasos, start=1):
        bloques.append(f"**Paso {j} — {paso.titulo}**\n\n{paso.detalle}")
    if ej.respuesta:
        bloques.append(f"### Respuesta\n\n{ej.respuesta}")
    if ej.observacion:
        bloques.append(f"### Por qué / errores típicos\n\n{ej.observacion}")
    if ej.verificacion:
        bloques.append(f"> ✔ *Verificación automática:* {ej.verificacion}")
    return "\n\n".join(bloques)


def a_texto(examen: Dict, con_soluciones: bool = True) -> str:
    """Versión sin marcas de Markdown, para leer en la terminal."""
    texto = a_markdown(examen, con_soluciones)
    texto = re.sub(r"^#{1,6}\s*", "", texto, flags=re.MULTILINE)
    texto = texto.replace("**", "").replace("`", "")
    return texto


# ==========================================================================
# HTML
# ==========================================================================

def _inline(texto: str) -> str:
    """Negritas y código en línea, escapando el resto."""
    partes = re.split(r"(`[^`]*`)", texto)
    salida = []
    for parte in partes:
        if parte.startswith("`") and parte.endswith("`") and len(parte) > 1:
            salida.append(f"<code>{_html.escape(parte[1:-1])}</code>")
        else:
            escapado = _html.escape(parte)
            escapado = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escapado)
            escapado = re.sub(r"(?<!\w)\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", escapado)
            salida.append(escapado)
    return "".join(salida)


def markdown_a_html(texto: str) -> str:
    """Conversor mínimo: encabezados, listas, tablas, citas y bloques de código."""
    lineas = texto.split("\n")
    salida: List[str] = []
    i = 0
    while i < len(lineas):
        linea = lineas[i]

        # Bloque de código (o diagrama mermaid)
        if linea.strip().startswith("```"):
            lenguaje = linea.strip()[3:].strip()
            i += 1
            cuerpo = []
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                cuerpo.append(lineas[i])
                i += 1
            i += 1
            contenido = "\n".join(cuerpo)
            if lenguaje == "mermaid":
                salida.append(f'<pre class="mermaid">{_html.escape(contenido)}</pre>')
            else:
                salida.append(f"<pre><code>{_html.escape(contenido)}</code></pre>")
            continue

        # Tabla
        if linea.strip().startswith("|") and i + 1 < len(lineas) and set(
            lineas[i + 1].replace("|", "").replace(" ", "")
        ) <= {"-", ":"} and lineas[i + 1].strip().startswith("|"):
            encabezado = [c.strip() for c in linea.strip().strip("|").split("|")]
            i += 2
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                filas.append([c.strip() for c in lineas[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{_inline(c)}</th>" for c in encabezado)
            trs = "".join(
                "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in fila) + "</tr>"
                for fila in filas
            )
            salida.append(f"<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>")
            continue

        # Encabezados
        encabezado = re.match(r"^(#{1,6})\s+(.*)$", linea)
        if encabezado:
            nivel = len(encabezado.group(1))
            salida.append(f"<h{nivel}>{_inline(encabezado.group(2))}</h{nivel}>")
            i += 1
            continue

        # Cita
        if linea.strip().startswith(">"):
            cuerpo = []
            while i < len(lineas) and lineas[i].strip().startswith(">"):
                cuerpo.append(lineas[i].strip()[1:].strip())
                i += 1
            salida.append(f"<blockquote>{_inline(' '.join(cuerpo))}</blockquote>")
            continue

        # Listas
        if re.match(r"^\s*[-*]\s+", linea):
            items = []
            while i < len(lineas) and re.match(r"^\s*[-*]\s+", lineas[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lineas[i]))
                i += 1
            salida.append("<ul>" + "".join(f"<li>{_inline(t)}</li>" for t in items) + "</ul>")
            continue
        if re.match(r"^\s*\d+[.)]\s+", linea):
            items = []
            while i < len(lineas) and re.match(r"^\s*\d+[.)]\s+", lineas[i]):
                items.append(re.sub(r"^\s*\d+[.)]\s+", "", lineas[i]))
                i += 1
            salida.append("<ol>" + "".join(f"<li>{_inline(t)}</li>" for t in items) + "</ol>")
            continue

        # Separador
        if linea.strip() == "---":
            salida.append("<hr>")
            i += 1
            continue

        # Párrafo
        if linea.strip():
            cuerpo = []
            while i < len(lineas) and lineas[i].strip() and not re.match(
                r"^\s*([-*]\s+|\d+[.)]\s+|#{1,6}\s+|>|\|)", lineas[i]
            ) and not lineas[i].strip().startswith("```") and lineas[i].strip() != "---":
                cuerpo.append(lineas[i])
                i += 1
            salida.append("<p>" + _inline("<br>".join(cuerpo)).replace("&lt;br&gt;", "<br>") + "</p>")
            continue
        i += 1
    return "\n".join(salida)


ESTILO = """
:root { color-scheme: light dark; --tinta:#16181d; --fondo:#fbfaf7; --suave:#5b6270;
        --borde:#e2e0da; --acento:#7c4dff; --caja:#ffffff; --ok:#0d7a4a; }
@media (prefers-color-scheme: dark) {
  :root { --tinta:#e9e7e2; --fondo:#15161a; --suave:#a1a7b4; --borde:#2c2f38;
          --acento:#b39dff; --caja:#1c1e24; --ok:#4ade80; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--fondo); color:var(--tinta); font-size:16px;
       font-family:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;
       line-height:1.65; }
.hoja { max-width: 46rem; margin: 0 auto; padding: 3rem 1.25rem 6rem; }
h1 { font-size:2rem; line-height:1.2; margin:0 0 .4rem; letter-spacing:-.01em; }
h2 { font-size:1.3rem; margin:2.6rem 0 .8rem; padding-top:1.2rem;
     border-top:1px solid var(--borde); }
h3 { font-size:1.02rem; margin:1.8rem 0 .5rem; color:var(--acento);
     text-transform:uppercase; letter-spacing:.07em;
     font-family:ui-sans-serif,system-ui,sans-serif; }
p { margin:.7rem 0; }
code { font-family:ui-monospace,'SF Mono',Menlo,Consolas,monospace; font-size:.9em;
       background:color-mix(in srgb, var(--acento) 10%, transparent);
       padding:.1em .35em; border-radius:4px; }
pre { background:var(--caja); border:1px solid var(--borde); border-radius:10px;
      padding:1rem; overflow-x:auto; }
pre code { background:none; padding:0; font-size:.88em; line-height:1.5; }
blockquote { margin:1.2rem 0; padding:.7rem 1rem; border-left:3px solid var(--acento);
             background:var(--caja); border-radius:0 8px 8px 0; color:var(--suave);
             font-size:.93em; }
table { border-collapse:collapse; width:100%; margin:1rem 0; font-size:.92em; }
th, td { border:1px solid var(--borde); padding:.45rem .7rem; text-align:left; }
th { background:var(--caja); font-family:ui-sans-serif,system-ui,sans-serif;
     font-size:.85em; text-transform:uppercase; letter-spacing:.05em; }
ul, ol { padding-left:1.4rem; }
li { margin:.3rem 0; }
hr { border:none; border-top:1px solid var(--borde); margin:2.5rem 0; }
.meta { color:var(--suave); font-size:.9em; font-family:ui-sans-serif,system-ui,sans-serif; }
.mermaid { text-align:center; background:var(--caja); }
@media print { body { background:#fff; } .hoja { max-width:none; padding:0; } }
"""


def a_html(examen: Dict, con_soluciones: bool = True, soluciones_aparte: bool = False) -> str:
    cuerpo = markdown_a_html(a_markdown(examen, con_soluciones, soluciones_aparte))
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_html.escape(examen['titulo'])} — Matemática I</title>
<style>{ESTILO}</style>
</head>
<body>
<div class="hoja">
{cuerpo}
</div>
<script type="module">
  // Los diagramas de Hasse se dibujan con mermaid si hay conexión; si no,
  // queda el diagrama por niveles en texto, que dice lo mismo.
  try {{
    const m = await import('https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs');
    const oscuro = matchMedia('(prefers-color-scheme: dark)').matches;
    m.default.initialize({{ startOnLoad: true, theme: oscuro ? 'dark' : 'default' }});
  }} catch (e) {{ /* sin conexión: no pasa nada */ }}
</script>
</body>
</html>"""
