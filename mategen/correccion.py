"""Corrección de las respuestas del modo práctica.

Vive en el paquete y no en la capa HTTP por dos motivos: se puede testear sin
levantar un servidor, y la corrección es matemática, no transporte.

Como el generador es determinístico, para corregir alcanza con volver a generar
el mismo examen a partir de la semilla: no hay que guardar nada en ninguna base
de datos.
"""

from typing import Any, Dict, List, Optional

# Cada corrector recibe (practica, respuesta) y devuelve la lista de resultados
# por ítem: [{"correcto": bool, "esperado": ..., "dado": ...}, ...]


def _normalizar_lista(valor) -> List:
    if valor is None:
        return []
    if isinstance(valor, list):
        return valor
    return [valor]


def _iguales_conjunto(a, b) -> bool:
    """Compara respuestas que son conjuntos de números, sin importar el orden."""
    try:
        return sorted(int(x) for x in _normalizar_lista(a)) == sorted(
            int(x) for x in _normalizar_lista(b)
        )
    except (TypeError, ValueError):
        return False


def _numero(valor) -> Optional[float]:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _vacio(valor) -> bool:
    """¿El alumno dejó esto sin contestar?

    Ojo con los falsos vacíos: en verdadero/falso, `False` es una respuesta; en
    numérica, `0` también. Sólo cuentan como vacíos None y la cadena vacía.
    """
    return valor is None or (isinstance(valor, str) and not valor.strip())


def corregir(practica: Dict, respuesta: Any) -> Dict:
    """Corrige un ejercicio. Devuelve aciertos, total y el detalle por ítem.

    Cada ítem del detalle informa `respondido`: no es lo mismo equivocarse que
    dejar en blanco. Quien deja en blanco no debería recibir la respuesta
    servida —sería regalarle el ejercicio por apretar Corregir sin querer—, y el
    frontend usa ese dato para mostrar «sin responder» en vez del resultado.
    """
    tipo = (practica or {}).get("tipo")
    if not tipo:
        return {"aciertos": 0, "total": 0, "detalle": [], "sin_correccion": True}

    detalle: List[Dict] = []

    if tipo in ("verdadero-falso", "nombrar-ley", "nombrar-regla"):
        dadas = _normalizar_lista(respuesta)
        for i, item in enumerate(practica.get("items", [])):
            dado = dadas[i] if i < len(dadas) else None
            respondido = not _vacio(dado)
            detalle.append({
                "esperado": item["correcta"],
                "dado": dado,
                "respondido": respondido,
                "correcto": respondido and dado == item["correcta"],
                "etiqueta": item.get("enunciado") or _etiqueta_ley(item),
            })

    elif tipo == "numerica":
        dadas = _normalizar_lista(respuesta)
        for i, item in enumerate(practica.get("items", [])):
            crudo = dadas[i] if i < len(dadas) else None
            respondido = not _vacio(crudo)
            dado = _numero(crudo) if respondido else None
            detalle.append({
                "esperado": item["valor"],
                "dado": dado,
                "respondido": respondido,
                "correcto": dado is not None and dado == float(item["valor"]),
                "etiqueta": item["texto"],
            })

    elif tipo == "propiedades":
        # Acá el formulario entero es una sola respuesta: si el alumno tocó algo,
        # lo que dejó sin marcar significa "no la cumple", que es justo lo que
        # promete la interfaz. Si no tocó nada, no contestó.
        correctas = practica.get("correctas", {})
        respondido = isinstance(respuesta, dict)
        dadas = respuesta if respondido else {}
        for nombre in practica.get("propiedades", []):
            esperado = correctas.get(nombre)
            dado = bool(dadas.get(nombre, False)) if respondido else None
            detalle.append({
                "esperado": esperado,
                "dado": dado,
                "respondido": respondido,
                "correcto": respondido and dado == bool(esperado),
                "etiqueta": nombre,
            })

    elif tipo == "si-no":
        esperado = practica.get("correcta")
        respondido = respuesta is not None
        detalle.append({
            "esperado": esperado,
            "dado": respuesta,
            "respondido": respondido,
            "correcto": respondido and bool(respuesta) == bool(esperado),
            "etiqueta": practica.get("pregunta", ""),
        })

    elif tipo == "opcion-multiple":
        esperado = practica.get("correcta")
        respondido = isinstance(respuesta, int) and not isinstance(respuesta, bool)
        dado = respuesta if respondido else None
        detalle.append({
            "esperado": esperado,
            "dado": dado,
            "respondido": respondido,
            "correcto": respondido and dado == esperado,
            "etiqueta": practica.get("pregunta", ""),
        })

    elif tipo == "elementos-particulares":
        # Acá None es una respuesta legítima ("no tiene"), así que no alcanza
        # con mirar si el valor es nulo: hay que ver si la clave está.
        dadas = respuesta if isinstance(respuesta, dict) else {}
        for pregunta in practica.get("preguntas", []):
            esperado = pregunta["correcta"]
            respondido = pregunta["clave"] in dadas
            dado = dadas.get(pregunta["clave"]) if respondido else None
            detalle.append({
                "esperado": esperado,
                "dado": dado,
                "respondido": respondido,
                "correcto": respondido and dado == esperado,
                "etiqueta": pregunta["texto"],
            })

    elif tipo == "conjuntos-por-extension":
        correctas = practica.get("correctas", {})
        dadas = respuesta if isinstance(respuesta, dict) else {}
        for campo in practica.get("campos", []):
            esperado = correctas.get(campo, [])
            dado = dadas.get(campo)
            respondido = not _vacio(dado)
            detalle.append({
                "esperado": esperado,
                "dado": dado,
                "respondido": respondido,
                "correcto": respondido and _iguales_conjunto(dado, esperado),
                "etiqueta": campo,
            })

    elif tipo == "emparejar":
        correctas = practica.get("correctas", [])
        dadas = _normalizar_lista(respuesta)
        for i, izquierda in enumerate(practica.get("izquierda", [])):
            esperado = correctas[i] if i < len(correctas) else None
            dado = dadas[i] if i < len(dadas) else None
            respondido = not _vacio(dado)
            detalle.append({
                "esperado": esperado,
                "dado": dado,
                "respondido": respondido,
                "correcto": respondido and dado == esperado,
                "etiqueta": izquierda,
            })

    else:
        return {"aciertos": 0, "total": 0, "detalle": [], "sin_correccion": True}

    aciertos = sum(1 for d in detalle if d["correcto"])
    return {"aciertos": aciertos, "total": len(detalle), "detalle": detalle}


def _etiqueta_ley(item: Dict) -> str:
    despues = item.get("despues") or {}
    return despues.get("texto", "")


def corregir_examen(examen: Dict, respuestas: List[Any]) -> Dict:
    """Corrige un examen completo ya generado.

    `respuestas[i]` corresponde al ejercicio i. El puntaje de cada ejercicio se
    reparte en proporción a los ítems acertados.
    """
    resultados = []
    puntos = 0.0
    puntos_totales = 0
    for i, ejercicio in enumerate(examen["ejercicios"]):
        respuesta = respuestas[i] if i < len(respuestas) else None
        resultado = corregir(ejercicio.practica, respuesta)
        obtenidos = (
            ejercicio.puntaje * resultado["aciertos"] / resultado["total"]
            if resultado["total"]
            else 0.0
        )
        puntos += obtenidos
        puntos_totales += ejercicio.puntaje
        resultados.append({
            "ejercicio": i,
            "subtema": ejercicio.subtema,
            "puntaje": ejercicio.puntaje,
            "obtenidos": round(obtenidos, 2),
            **resultado,
        })
    return {
        "puntos": round(puntos, 2),
        "puntos_totales": puntos_totales,
        "aprobado": puntos >= 0.6 * puntos_totales if puntos_totales else False,
        "ejercicios": resultados,
    }
