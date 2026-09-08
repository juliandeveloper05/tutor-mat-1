"""Armado de exámenes: convierte cada generador en un Ejercicio completo.

Un Ejercicio trae el enunciado, la resolución paso a paso con la justificación de
cada propiedad usada, una observación pedagógica (el "por qué" y los errores
típicos) y la nota de cómo se verificó la respuesta por computadora.
"""

import random
import zlib
from typing import Callable, Dict, List

from . import serial
from .conjuntos import expr as cexpr
from .conjuntos import extension as cext
from .conjuntos import venn as cvenn
from .ejercicio import Ejercicio
from .funciones import biyectiva as fbiy
from .funciones import composicion as fcomp
from .funciones import dominio as fdom
from .logica import cuantificadores as lcuant
from .logica import derivacion as lder
from .logica import leyes as lleyes
from .logica.formula import escribir, tabla_markdown
from .relaciones import equivalencia as req
from .relaciones import orden as rord
from .relaciones import propiedades as rprop


# ==========================================================================
# Ayudas para el modo práctica
# ==========================================================================

def _azar_estable(*partes: str) -> random.Random:
    """Un generador determinístico derivado del contenido, no del examen.

    Importa que la práctica **no** consuma azar del rng del examen: si lo
    hiciera, agregar o quitar una opción cambiaría todos los ejercicios
    siguientes y una misma semilla dejaría de dar el mismo examen que antes.
    Se usa crc32 y no hash() porque hash() de un str cambia en cada proceso.
    """
    semilla = zlib.crc32("|".join(partes).encode("utf-8"))
    return random.Random(semilla)


def _opciones(correcta: str, alternativas: List[str], cantidad: int = 4) -> Dict:
    """Arma una lista de opciones con una sola correcta, ya mezclada.

    Devuelve {"opciones": [...], "correcta": índice}. Las alternativas que
    coinciden con la respuesta correcta se descartan, así nunca hay dos
    opciones válidas.
    """
    distintas = [a for a in dict.fromkeys(alternativas) if a != correcta]
    rng = _azar_estable(correcta, *distintas)
    rng.shuffle(distintas)
    opciones = [correcta] + distintas[: max(0, cantidad - 1)]
    rng.shuffle(opciones)
    return {"opciones": opciones, "correcta": opciones.index(correcta)}


def _practica_leyes(pasos, nombres_ley: List[str]) -> Dict:
    """Práctica común a simplificación e igualdades: nombrar la ley de cada paso.

    Es exactamente lo que la cátedra exige y lo que más puntos cuesta olvidar:
    una cadena sin los nombres de las leyes no suma.
    """
    items = []
    for datos in pasos:
        ley = datos["ley"]
        items.append({
            "antes": datos["antes"],
            "despues": datos["despues"],
            **_opciones(ley, list(nombres_ley)),
        })
    return {"tipo": "nombrar-ley", "items": items}


# ==========================================================================
# LÓGICA
# ==========================================================================

def ej_simplificacion(rng: random.Random) -> Ejercicio:
    enunciado, resultado, pasos = lleyes.generar_simplificacion(rng)
    ej = Ejercicio(
        tema="Lógica",
        subtema="Simplificación con leyes lógicas",
        consigna=(
            "Obtener una forma proposicional más simple equivalente a la dada, "
            "utilizando leyes lógicas. Indicar en cada paso la ley aplicada.\n\n"
            f"**{escribir(enunciado)}**"
        ),
        puntaje=15,
    )
    ej.agregar(
        "Cómo encarar el ejercicio",
        "No hay que adivinar el resultado: se avanza aplicando leyes **una por vez** y "
        "justificando cada una. La estrategia que casi siempre funciona es:\n\n"
        "1. Sacar de encima los conectivos → y ↔ (leyes del condicional y del "
        "bicondicional), porque las demás leyes están escritas con ∧, ∨ y ¬.\n"
        "2. Empujar las negaciones hacia adentro con De Morgan y eliminar dobles "
        "negaciones.\n"
        "3. Recién ahí buscar las leyes que **achican**: complemento, identidad, "
        "dominación, absorción, idempotencia.",
    )
    cadena = [f"    {escribir(enunciado)}"]
    for i, (ley, _antes, _despues, completa) in enumerate(pasos, start=1):
        cadena.append(f"  ≡ {escribir(completa)}        ({i}) {ley}")
    ej.agregar(
        "Cadena de equivalencias",
        "```\n" + "\n".join(cadena) + "\n```",
    )
    detalles = []
    for i, (ley, antes, despues, _completa) in enumerate(pasos, start=1):
        detalles.append(
            f"**({i}) {ley}.** Se reemplazó `{escribir(antes)}` por `{escribir(despues)}`. "
            + _explicar_ley(ley)
        )
    ej.agregar("Justificación de cada paso", "\n\n".join(detalles))
    ej.respuesta = f"**{escribir(resultado)}**"
    ej.observacion = (
        "Dos errores frecuentes: (a) aplicar De Morgan sin negar *los dos* términos "
        "—recordar que ¬(p ∧ q) es ¬p ∨ ¬q, con el conectivo cambiado—; y (b) dar por "
        "terminado el ejercicio sin escribir qué ley se usó. La cátedra pide la "
        "justificación: una cadena de equivalencias sin nombres no suma puntaje."
    )
    ej.verificacion = (
        "La equivalencia entre el enunciado y el resultado se comprobó con la tabla de "
        "verdad completa (todas las valuaciones posibles)."
    )
    pasos_json = [
        {
            "ley": ley,
            "antes": serial.formula_completa(antes),
            "despues": serial.formula_completa(despues),
            "completa": serial.formula_completa(completa),
        }
        for ley, antes, despues, completa in pasos
    ]
    ej.visual = {
        "tipo": "cadena-logica",
        "inicial": serial.formula_completa(enunciado),
        "final": serial.formula_completa(resultado),
        "pasos": pasos_json,
    }
    ej.practica = _practica_leyes(
        pasos_json, [nombre for nombre, _ley in lleyes.LEYES]
    )
    return ej


_EXPLICACIONES = {
    "Ley del condicional": "Un condicional p → q es falso solamente cuando el antecedente es "
    "verdadero y el consecuente falso; eso es exactamente lo que dice ¬p ∨ q.",
    "Ley del bicondicional": "p ↔ q equivale a exigir las dos implicaciones a la vez.",
    "Ley de De Morgan": "Negar una conjunción da la disyunción de las negaciones (y viceversa): "
    "el conectivo se da vuelta.",
    "Doble negación": "Negar dos veces devuelve la proposición original.",
    "Negación de una constante": "¬V es F y ¬F es V.",
    "Ley del complemento": "p ∧ ¬p nunca puede ser verdadera (es F) y p ∨ ¬p siempre lo es (es V), "
    "sin importar el valor de p.",
    "Ley de identidad": "V es neutro de la conjunción y F es neutro de la disyunción.",
    "Ley de dominación": "V absorbe a la disyunción y F absorbe a la conjunción.",
    "Idempotencia": "Repetir la misma proposición en una ∧ o en una ∨ no aporta información.",
    "Ley de absorción": "Si un término ya aparece solo, el paréntesis que lo contiene no cambia "
    "el valor de verdad.",
    "Ley de absorción (2ª forma)": "p ∨ (¬p ∧ q) ≡ p ∨ q: cuando p es falsa, lo único que puede "
    "salvar la disyunción es q.",
    "Ley distributiva (factor común)": "Se saca factor común, igual que en álgebra.",
    "Definición de diferencia (A − B = A ∩ B̅)": "Estar en A − B es estar en A y no estar en B.",
    "Doble complemento": "El complemento del complemento devuelve el conjunto original.",
    "Complemento de U y de ∅": "El complemento de U es ∅ y el de ∅ es U.",
}


def _explicar_ley(nombre: str) -> str:
    return _EXPLICACIONES.get(nombre, "")


def ej_derivacion(rng: random.Random) -> Ejercicio:
    premisas, meta, prueba = lder.generar_derivacion(rng)
    texto_premisas = "\n".join(f"{i}) {escribir(p)}" for i, p in enumerate(premisas, 1))
    ej = Ejercicio(
        tema="Lógica",
        subtema="Validez de un razonamiento (método de derivaciones)",
        consigna=(
            "Usando el método de derivaciones, probar que el siguiente razonamiento es "
            "válido:\n\n```\n" + texto_premisas + f"\n∴ {escribir(meta)}\n```"
        ),
        puntaje=15,
    )
    ej.agregar(
        "Qué hay que probar",
        "Un razonamiento es **válido** cuando no existe ninguna valuación que haga "
        "verdaderas a todas las premisas y falsa a la conclusión. El método de "
        "derivaciones prueba eso sin construir la tabla: se parte de las premisas y se "
        "van deduciendo renglones nuevos con reglas de inferencia, hasta llegar a la "
        "conclusión. Cada renglón debe indicar **qué regla** se usó y **sobre qué "
        "renglones**.",
    )
    ej.agregar("Derivación", lder.formatear(prueba))
    usadas = sorted({regla for _, regla, refs in prueba if refs})
    ej.agregar(
        "Reglas utilizadas",
        "\n".join(f"- **{r}**: {_REGLAS[r]}" for r in usadas if r in _REGLAS),
    )
    ej.respuesta = (
        f"Se llegó a **{escribir(meta)}** partiendo únicamente de las premisas, "
        f"así que el razonamiento es **válido**."
    )
    ej.observacion = (
        "Conviene mirar primero la conclusión y preguntarse de qué renglón podría salir. "
        "Si la conclusión aparece como consecuente de una implicación, hay que conseguir "
        "su antecedente (Modus Ponens). Si aparece dentro de una disyunción, hay que negar "
        "el otro término (Silogismo Disyuntivo). Trabajar hacia atrás y después escribir "
        "la derivación hacia adelante es más rápido que probar reglas al azar."
    )
    ej.verificacion = (
        "La derivación fue hallada por el programa usando sólo reglas de inferencia, y "
        "además se confirmó con la tabla de verdad que (P₁ ∧ … ∧ Pₙ) → C es una tautología."
    )
    renglones = [
        {
            "n": i,
            "formula": serial.formula_completa(formula),
            "regla": regla,
            "refs": refs,
        }
        for i, (formula, regla, refs) in enumerate(prueba, start=1)
    ]
    ej.visual = {
        "tipo": "derivacion",
        "premisas": [serial.formula_completa(p) for p in premisas],
        "meta": serial.formula_completa(meta),
        "renglones": renglones,
    }
    # Se pregunta la regla sólo en los renglones deducidos, no en las premisas.
    ej.practica = {
        "tipo": "nombrar-regla",
        "items": [
            {
                "n": r["n"],
                "formula": r["formula"],
                "refs": r["refs"],
                **_opciones(r["regla"], list(_REGLAS)),
            }
            for r in renglones
            if r["refs"]
        ],
    }
    return ej


_REGLAS = {
    "Modus Ponens": "de p → q y p se deduce q.",
    "Modus Tollens": "de p → q y ¬q se deduce ¬p.",
    "Silogismo hipotético": "de p → q y q → r se deduce p → r.",
    "Silogismo disyuntivo": "de p ∨ q y ¬p se deduce q.",
    "Simplificación": "de p ∧ q se deduce p (y también q).",
    "Conjunción": "de p y q se deduce p ∧ q.",
    "Doble negación": "de ¬¬p se deduce p.",
    "Ley del condicional": "¬p ∨ q equivale a p → q.",
}


def ej_cuantificadores(rng: random.Random) -> Ejercicio:
    preds, items = lcuant.generar_items(rng)
    lista_preds = "\n".join(f"- {p.nombre}(x): {p.texto}" for p in preds)
    incisos = "\n".join(
        f"{chr(ord('a') + i)}) {it.enunciado}" for i, it in enumerate(items)
    )
    ej = Ejercicio(
        tema="Lógica",
        subtema="Cuantificadores y conjuntos de verdad",
        consigna=(
            "Sean las siguientes proposiciones abiertas, con universo U = ℤ (todos los "
            f"números enteros):\n\n{lista_preds}\n\n"
            "Determinar la verdad o falsedad de cada una de las siguientes proposiciones. "
            "Dar un contraejemplo o una explicación, según corresponda.\n\n"
            f"{incisos}"
        ),
        puntaje=10,
    )
    ej.agregar(
        "Paso previo: los conjuntos de verdad",
        "Antes de decidir nada conviene escribir el conjunto de verdad de cada predicado, "
        "es decir qué enteros lo hacen verdadero:\n\n"
        + "\n".join(f"- V({p.nombre}) = {p.verdad_texto()}" for p in preds)
        + "\n\nCon esto a la vista, cada inciso se resuelve casi solo.",
    )
    ej.agregar(
        "Criterio para decidir",
        "- Para **refutar un ∀** alcanza con **un** contraejemplo: un valor del universo "
        "donde el cuerpo del cuantificador sea falso.\n"
        "- Para **probar un ∃** alcanza con **un** testigo.\n"
        "- Para **probar un ∀** no alcanza con ejemplos: hay que cubrir todo el universo. "
        "Cuando el antecedente tiene conjunto de verdad finito se puede hacer caso por "
        "caso, porque fuera de ese conjunto el condicional es verdadero por tener "
        "antecedente falso.\n"
        "- Para **refutar un ∃** hay que descartar todo el universo, y de nuevo el truco "
        "es apoyarse en el predicado de conjunto de verdad finito.",
    )
    for i, it in enumerate(items):
        ej.agregar(
            f"Inciso {chr(ord('a') + i)}) {it.enunciado}",
            it.justificacion,
        )
    ej.respuesta = "  ".join(
        f"**{chr(ord('a') + i)})** {'V' if it.valor else 'F'}" for i, it in enumerate(items)
    )
    ej.observacion = (
        "El error más común es contestar sólo «verdadero» o «falso». La consigna pide "
        "justificar: si es falsa, hay que **escribir el contraejemplo**; si es verdadera, "
        "explicar por qué vale para todo el universo. También hay que tener cuidado con el "
        "condicional de antecedente falso: ∀x: [p(x) → q(x)] es verdadera «por vacuidad» "
        "cuando ningún x cumple p(x)."
    )
    ej.verificacion = (
        "Cada inciso se evaluó sobre todos los enteros de −120 a 120; el contraejemplo o "
        "testigo informado es el de menor módulo, y las justificaciones universales sólo "
        "se emiten cuando la verificación es completa (conjunto de verdad finito)."
    )
    # Para dibujar la recta numérica alcanza con una ventana chica: los
    # predicados del banco ya se estabilizaron mucho antes de ±12.
    ventana = list(range(-12, 13))
    ej.visual = {
        "tipo": "cuantificadores",
        "ventana": ventana,
        "predicados": [
            {
                "nombre": p.nombre,
                "texto": p.texto,
                "finito": p.finito,
                "conjunto_verdad": p.verdad_texto(),
                "puntos": [x for x in ventana if p.func(x)],
                "todos_los_puntos": p.conjunto_verdad() if p.finito else None,
            }
            for p in preds
        ],
        "items": [
            {
                "enunciado": it.enunciado,
                "valor": it.valor,
                "cuant": it.cuant,
                "forma": it.forma,
                "predicados": [it.p.nombre, it.q.nombre],
                "puntos": [x for x in ventana
                           if lcuant._eval_cuerpo(it.forma, it.p, it.q, x)],
            }
            for it in items
        ],
    }
    ej.practica = {
        "tipo": "verdadero-falso",
        "items": [
            {"enunciado": it.enunciado, "correcta": it.valor} for it in items
        ],
    }
    return ej


# ==========================================================================
# CONJUNTOS
# ==========================================================================

def ej_conjuntos_extension(rng: random.Random) -> Ejercicio:
    d = cext.generar(rng)
    datos = "\n".join(f"- {k} = {v}" for k, v in d["datos"])
    ej = Ejercicio(
        tema="Conjuntos",
        subtema="Determinar conjuntos por extensión",
        consigna=(
            "Determinar por extensión los conjuntos A, B y C a partir de la siguiente "
            f"información, y ubicar los elementos en un diagrama de Venn.\n\n{datos}"
        ),
        puntaje=15,
    )
    for titulo, detalle in d["pasos"]:
        ej.agregar(titulo, detalle)
    regiones = "\n".join(
        f"- {nombre}: " + ("∅" if not v else "{" + ", ".join(str(x) for x in sorted(v)) + "}")
        for nombre, v in d["regiones"].items()
    )
    ej.agregar(
        "Ubicación en el diagrama de Venn",
        "Cada elemento va en una sola región, según a qué conjuntos pertenece:\n\n" + regiones,
    )
    ej.respuesta = f"A = {d['texto_A']}   B = {d['texto_B']}   C = {d['texto_C']}"
    ej.observacion = (
        "La clave es no adivinar: cada conjunto se reconstruye a partir de una identidad "
        "que vale siempre, como C = (C − B) ∪ (C ∩ B). Conviene además **verificar al "
        "final**: recalcular con los conjuntos hallados cada dato del enunciado y "
        "comprobar que coincide."
    )
    ej.verificacion = (
        "El programa recalculó todos los datos del enunciado a partir de los conjuntos "
        "hallados y verificó que coinciden exactamente."
    )
    ej.visual = {
        "tipo": "venn-elementos",
        "letras": ["A", "B", "C"],
        "conjuntos": {
            "A": sorted(d["A"]), "B": sorted(d["B"]), "C": sorted(d["C"]),
        },
        # Cada elemento va en una sola región: es lo que se dibuja.
        "regiones": {
            "a": sorted(d["A"] - d["B"] - d["C"]),
            "b": sorted(d["B"] - d["A"] - d["C"]),
            "c": sorted(d["C"] - d["A"] - d["B"]),
            "ab": sorted((d["A"] & d["B"]) - d["C"]),
            "ac": sorted((d["A"] & d["C"]) - d["B"]),
            "bc": sorted((d["B"] & d["C"]) - d["A"]),
            "abc": sorted(d["A"] & d["B"] & d["C"]),
        },
        "datos": [{"clave": k, "valor": v} for k, v in d["datos"]],
    }
    ej.practica = {
        "tipo": "conjuntos-por-extension",
        "campos": ["A", "B", "C"],
        "correctas": {
            "A": sorted(d["A"]), "B": sorted(d["B"]), "C": sorted(d["C"]),
        },
    }
    return ej


def ej_venn(rng: random.Random) -> Ejercicio:
    d = cvenn.generar(rng)
    datos = "; ".join(d["datos"])
    preguntas = "\n".join(
        f"{chr(ord('a') + i)}) {p['texto']}" for i, p in enumerate(d["preguntas"])
    )
    ej = Ejercicio(
        tema="Conjuntos",
        subtema="Problema de conteo con diagrama de Venn",
        consigna=(
            f"{d['intro']} Se obtuvieron estos datos: {datos}.\n\n"
            f"{d['contexto']['letra_conjuntos']}, responder:\n\n{preguntas}"
        ),
        puntaje=15,
    )
    for titulo, detalle in d["pasos"]:
        ej.agregar(titulo, detalle)
    for i, p in enumerate(d["preguntas"]):
        detalle = (
            f"Expresión de conjuntos: `{p['expresion']}`\n\n"
            f"Cuenta: {p['cuenta']} = **{p['valor']}**"
        )
        if "descripcion" in p:
            detalle += f"\n\nEn lenguaje cotidiano, {p['descripcion']}."
        ej.agregar(f"Inciso {chr(ord('a') + i)})", detalle)
    ej.respuesta = "   ".join(
        f"**{chr(ord('a') + i)})** {p['valor']}" for i, p in enumerate(d["preguntas"])
    )
    ej.observacion = (
        "El error clásico es sumar los datos como si fueran regiones disjuntas. Un dato "
        "como «en 34 se vende Tofin» incluye a los que además venden otras marcas. Por eso "
        "**siempre se empieza por el centro** del diagrama (los que están en los tres) y se "
        "va restando hacia afuera. Al terminar, la suma de las 8 regiones tiene que dar el "
        "total: es el control que conviene hacer antes de contestar."
    )
    ej.verificacion = (
        "Las regiones se eligieron antes de redactar el enunciado, así que el problema es "
        "consistente por construcción; el programa verificó además que suman el total y "
        "que cada respuesta coincide con las regiones correspondientes."
    )
    ctx = d["contexto"]
    ej.visual = {
        "tipo": "venn-conteo",
        "letras": list(ctx["letras"]),
        "nombres": list(ctx["elementos"]),
        "unidad": ctx["unidad"],
        "regiones": d["regiones"],
        "total": d["total"],
        # Qué regiones pinta cada pregunta, para resaltarlas al responder.
        "resaltados": [
            {"pregunta": i, "regiones": rs}
            for i, rs in enumerate([
                ["a", "b", "c"],
                ["b", "ab"],
                ["a", "ac", "b", "bc"],
            ])
        ],
    }
    ej.practica = {
        "tipo": "numerica",
        "items": [
            {"texto": p["texto"], "expresion": p["expresion"], "valor": p["valor"]}
            for p in d["preguntas"]
        ],
    }
    return ej


def ej_identidad_conjuntos(rng: random.Random) -> Ejercicio:
    enunciado, resultado, pasos = cexpr.generar_identidad(rng)
    ej = Ejercicio(
        tema="Conjuntos",
        subtema="Demostración de una igualdad de conjuntos",
        consigna=(
            "Usando una sucesión de igualdades y propiedades de conjuntos, demostrar "
            f"que:\n\n**{cexpr.escribir(enunciado)} = {cexpr.escribir(resultado)}**"
        ),
        puntaje=15,
    )
    ej.agregar(
        "Por qué se puede trabajar así",
        "Las operaciones entre conjuntos cumplen exactamente las mismas leyes que los "
        "conectivos lógicos: ∪ se comporta como ∨, ∩ como ∧ y el complemento como ¬. "
        "Por eso valen De Morgan, la distributiva, la absorción y el resto, y se puede "
        "demostrar la igualdad transformando un miembro hasta llegar al otro, sin recurrir "
        "a la doble inclusión.",
    )
    cadena = [f"    {cexpr.escribir(enunciado)}"]
    for i, (ley, expr) in enumerate(pasos, start=1):
        cadena.append(f"  = {cexpr.escribir(expr)}        ({i}) {ley}")
    ej.agregar("Cadena de igualdades", "```\n" + "\n".join(cadena) + "\n```")
    ej.agregar(
        "Justificación de cada paso",
        "\n\n".join(
            f"**({i}) {ley}.** " + _explicar_ley(ley)
            for i, (ley, _e) in enumerate(pasos, start=1)
        ),
    )
    ej.respuesta = (
        f"Partiendo del miembro izquierdo se llegó a {cexpr.escribir(resultado)}, "
        f"que es el miembro derecho. La igualdad queda demostrada."
    )
    ej.observacion = (
        "Conviene empezar por el miembro **más complicado** y simplificarlo; ir del simple "
        "al complicado obliga a adivinar. Y como en lógica, cada igualdad tiene que estar "
        "acompañada del nombre de la propiedad usada."
    )
    ej.verificacion = (
        "La igualdad se comprobó interpretando ambas expresiones en el álgebra de Boole "
        "libre: se calculó qué regiones del diagrama de Venn ocupa cada miembro y se "
        "verificó que son idénticas."
    )
    variables = sorted(
        set(cexpr.variables(enunciado)) | set(cexpr.variables(resultado))
    )
    pasos_json = [
        {"ley": ley, "completa": serial.expresion_completa(expr)}
        for ley, expr in pasos
    ]
    ej.visual = {
        "tipo": "cadena-conjuntos",
        "variables": variables,
        "inicial": serial.expresion_completa(enunciado),
        "final": serial.expresion_completa(resultado),
        "pasos": pasos_json,
        # Las regiones que pinta cada miembro: dibujadas lado a lado se ve que
        # son las mismas, que es exactamente cómo lo verifica el programa.
        "celdas_inicial": serial.celdas_a_json(enunciado, variables),
        "celdas_final": serial.celdas_a_json(resultado, variables),
    }
    ej.practica = _practica_leyes(
        [{"ley": p["ley"], "antes": None, "despues": p["completa"]} for p in pasos_json],
        sorted(set(cexpr.NOMBRE_LEY.values()) | {"Definición de diferencia (A − B = A ∩ B̅)"}),
    )
    return ej


# ==========================================================================
# RELACIONES
# ==========================================================================

def ej_relacion_propiedades(rng: random.Random) -> Ejercicio:
    d = rprop.generar(rng)
    ej = Ejercicio(
        tema="Relaciones",
        subtema="Propiedades de una relación",
        consigna=(
            f"Sea A = {{{', '.join(d['A'])}}} y la relación R definida en A por:\n\n"
            f"**R = {d['texto_R']}**\n\n"
            "a) Indicar si R es reflexiva, irreflexiva, simétrica, antisimétrica y/o "
            "transitiva. Justificar cada respuesta.\n"
            "b) Construir una relación reflexiva agregándole a R los pares necesarios.\n"
            "c) Construir una relación antisimétrica quitándole a R la menor cantidad "
            "posible de pares."
        ),
        puntaje=15,
    )
    ej.agregar(
        "a) Análisis de las propiedades",
        "Cada propiedad se decide revisando *todos* los casos, y se justifica exhibiendo "
        "el par que falla (si no se cumple) o explicando por qué se cumple siempre:\n\n"
        + d["analisis"],
    )
    ej.agregar(
        "b) Hacerla reflexiva",
        "Para ser reflexiva tienen que estar **todos** los pares (x, x) con x ∈ A. "
        f"Faltan {rprop.lista(d['agregar_reflexiva'])}, así que basta agregarlos:\n\n"
        f"R' = R ∪ {rprop.lista(d['agregar_reflexiva'])}\n\n"
        "Agregar pares nunca puede romper la reflexividad, así que R' es reflexiva.",
    )
    ej.agregar(
        "c) Hacerla antisimétrica",
        "La antisimetría falla cuando hay dos elementos **distintos** relacionados en "
        "ambos sentidos. Los pares conflictivos son "
        f"{rprop.lista(d['quitar_antisimetrica'])} junto con sus simétricos: por cada "
        "conflicto hay que sacar **uno** de los dos (da igual cuál).\n\n"
        f"Quitando {rprop.lista(d['quitar_antisimetrica'])} queda:\n\n"
        f"R'' = R − {rprop.lista(d['quitar_antisimetrica'])}\n\n"
        f"Son {len(d['quitar_antisimetrica'])} par(es), la cantidad mínima posible: con "
        "menos, algún conflicto quedaría sin resolver.",
    )
    ej.respuesta = d["analisis"]
    ej.observacion = (
        "Dos confusiones habituales. (1) «No reflexiva» **no** es lo mismo que "
        "«irreflexiva»: una relación puede tener algunos pares (x, x) y no todos, y "
        "entonces no es ni una cosa ni la otra. (2) Los pares (x, x) **no** rompen la "
        "antisimetría: la condición pide x ≠ y. Una relación puede ser simétrica y "
        "antisimétrica a la vez (por ejemplo, la relación identidad)."
    )
    ej.verificacion = (
        "El programa recorrió todos los pares de A × A para decidir cada propiedad, y "
        "comprobó que las relaciones corregidas de b) y c) efectivamente cumplen lo pedido."
    )
    ej.visual = {
        "tipo": "relacion",
        "A": d["A"],
        "pares": serial.pares_a_json(d["R"]),
        "propiedades": _propiedades_a_json(d["A"], d["R"]),
        "correcciones": {
            "agregar_reflexiva": serial.pares_a_json(d["agregar_reflexiva"]),
            "quitar_antisimetrica": serial.pares_a_json(d["quitar_antisimetrica"]),
            "agregar_simetrica": serial.pares_a_json(d["agregar_simetrica"]),
            "quitar_irreflexiva": serial.pares_a_json(d["quitar_irreflexiva"]),
        },
    }
    ej.practica = {
        "tipo": "propiedades",
        "propiedades": ["reflexiva", "irreflexiva", "simetrica", "antisimetrica", "transitiva"],
        "correctas": {
            nombre: rprop.analizar(d["A"], d["R"])[nombre][0]
            for nombre in ("reflexiva", "irreflexiva", "simetrica", "antisimetrica", "transitiva")
        },
    }
    return ej


def _propiedades_a_json(A: List[str], R) -> Dict:
    """Cada propiedad con su veredicto y los pares que lo justifican."""
    analisis = rprop.analizar(A, R)
    salida = {}
    for nombre, (vale, testigos) in analisis.items():
        if nombre == "transitiva":
            # Los testigos son ternas (par1, par2, par que falta).
            detalle = [
                {"primero": list(p1), "segundo": list(p2), "falta": list(falta)}
                for p1, p2, falta in testigos[:4]
            ]
        else:
            detalle = [list(p) for p in testigos[:4]]
        salida[nombre] = {"vale": vale, "testigos": detalle}
    return salida


def ej_relacion_equivalencia(rng: random.Random) -> Ejercicio:
    d = req.generar(rng)
    ej = Ejercicio(
        tema="Relaciones",
        subtema="Relación de equivalencia, clases y conjunto cociente",
        consigna=(
            f"Sea A = {{{', '.join(d['A'])}}} y la relación:\n\n**R = {d['texto_R']}**\n\n"
            "a) Determinar si R es una relación de equivalencia. Justificar.\n"
            "b) Si lo es, hallar todas las clases de equivalencia y el conjunto cociente. "
            "Si no lo es, indicar qué propiedad falla y qué habría que agregar."
        ),
        puntaje=15,
    )
    an = d["analisis"]
    lineas = []
    for prop in ("reflexiva", "simetrica", "transitiva"):
        ok, testigos = an[prop]
        nombre = {"reflexiva": "Reflexiva", "simetrica": "Simétrica", "transitiva": "Transitiva"}[prop]
        if ok:
            lineas.append(f"- **{nombre}: SÍ.**")
        elif prop == "transitiva":
            (p1, p2, falta) = testigos[0]
            lineas.append(
                f"- **{nombre}: NO.** Están {rprop.par(p1)} y {rprop.par(p2)}, "
                f"pero falta {rprop.par(falta)}."
            )
        elif prop == "reflexiva":
            lineas.append(
                f"- **{nombre}: NO.** Falta {rprop.par(testigos[0])}."
            )
        else:
            x, y = testigos[0]
            lineas.append(
                f"- **{nombre}: NO.** Está {rprop.par((x, y))} pero falta {rprop.par((y, x))}."
            )
    ej.agregar(
        "a) Las tres propiedades",
        "Una relación es de equivalencia si y sólo si es reflexiva, simétrica y "
        "transitiva. Hay que verificar las tres:\n\n" + "\n".join(lineas),
    )
    if d["es_equivalencia"]:
        clases_texto = "\n".join(
            f"- {req.texto_clase(x, c)}" for x, c in d["clases"].items()
        )
        cociente = "{" + ", ".join(
            "{" + ", ".join(b) + "}" for b in d["cociente"]
        ) + "}"
        ej.agregar(
            "b) Clases de equivalencia",
            "La clase de x es el conjunto de todos los elementos relacionados con x:\n\n"
            + clases_texto
            + "\n\nLos elementos de una misma clase tienen exactamente la misma clase: "
            "por eso hay menos clases distintas que elementos.",
        )
        ej.agregar(
            "b) Conjunto cociente",
            f"El conjunto cociente A/R junta las clases **distintas**:\n\n"
            f"A/R = {cociente}\n\n"
            "Observar que las clases son disjuntas dos a dos y su unión da todo A: "
            "**toda relación de equivalencia determina una partición** del conjunto, y "
            "recíprocamente.",
        )
        ej.respuesta = f"Sí es de equivalencia. A/R = {cociente}"
    else:
        rota = d["propiedad_rota"]
        ej.agregar(
            "b) Qué falla y cómo se arregla",
            f"R **no** es de equivalencia porque falla la propiedad **{rota}** (ver el "
            "contraejemplo de arriba). Agregando el par que falta —y todos los que hagan "
            "falta para cerrar también la transitividad— se obtiene la menor relación de "
            "equivalencia que contiene a R, cuyas clases son los bloques de la partición "
            + "{" + ", ".join("{" + ", ".join(b) + "}" for b in d["particion"]) + "}.",
        )
        ej.respuesta = f"No es de equivalencia: falla la propiedad {rota}."
    ej.observacion = (
        "Para la transitividad no alcanza con mirar «algunos» pares: hay que revisar todas "
        "las cadenas (x, y), (y, z). Un truco práctico es armar el diagrama de Venn o el "
        "grafo de la relación: si es de equivalencia, el grafo queda partido en grupos "
        "donde todos apuntan a todos, y esos grupos son las clases."
    )
    ej.verificacion = (
        "Las tres propiedades se decidieron recorriendo todos los pares y todas las cadenas "
        "posibles; cuando la relación es de equivalencia se verificó además que las clases "
        "forman una partición de A (disjuntas y de unión total)."
    )
    ej.visual = {
        "tipo": "equivalencia",
        "A": d["A"],
        "pares": serial.pares_a_json(d["R"]),
        "propiedades": _propiedades_a_json(d["A"], d["R"]),
        "es_equivalencia": d["es_equivalencia"],
        "propiedad_rota": d["propiedad_rota"],
        # Los bloques agrupan los nodos al dibujar el grafo de la relación.
        "clases": {x: c for x, c in d["clases"].items()} if d["es_equivalencia"] else None,
        "cociente": d["cociente"] if d["es_equivalencia"] else None,
        "particion": d["particion"],
    }
    ej.practica = {
        "tipo": "si-no",
        "pregunta": "¿R es una relación de equivalencia?",
        "correcta": d["es_equivalencia"],
    }
    return ej


def ej_relacion_orden(rng: random.Random) -> Ejercicio:
    o = rord.generar_orden(rng, n=6)
    especificaciones = [
        ({"con_maximo": False, "con_minimo": True}, "sin máximo y con mínimo"),
        ({"con_maximo": True, "con_minimo": False}, "con máximo y sin mínimo"),
        ({"con_maximo": False, "con_minimo": False}, "sin máximo y sin mínimo"),
    ]
    rng.shuffle(especificaciones)
    elegido = None
    for spec, texto in especificaciones:
        for tam in (3, 4):
            B = rord.buscar_subconjunto(o, rng, tam, spec)
            if B:
                elegido = (B, texto, tam)
                break
        if elegido:
            break
    if elegido is None:  # el orden generado siempre admite alguna: red de seguridad
        elegido = (sorted(o.elems[:3]), "y analizar sus elementos particulares", 3)
    B, texto_spec, tam = elegido

    ej = Ejercicio(
        tema="Relaciones",
        subtema="Relación de orden y diagrama de Hasse",
        consigna=(
            "Se define en A = {" + ", ".join(o.etiquetas[e] for e in o.elems) + "} una "
            "relación de orden ≼ cuyo diagrama de Hasse está dado por las siguientes "
            "relaciones de cubrimiento (x ≺ y significa que y está inmediatamente por "
            f"encima de x):\n\n**{o.cubrimientos_texto()}**\n\n"
            "a) Indicar si se trata de un orden total o parcial. Justificar.\n"
            f"b) Hallar un subconjunto B de {tam} elementos {texto_spec} (indicar cuáles "
            "son los elementos particulares).\n"
            "c) Para ese B, hallar maximales, minimales, cotas superiores e inferiores, "
            "supremo e ínfimo."
        ),
        puntaje=15,
    )
    ej.agregar(
        "Cómo leer el diagrama de Hasse",
        "El diagrama sólo dibuja los **cubrimientos**: se sube por las líneas para leer la "
        "relación. x ≼ y si hay un camino ascendente de x a y (y además cada elemento se "
        "relaciona consigo mismo, por reflexividad). Los pares que se deducen por "
        "transitividad no se dibujan, para no llenar el diagrama de líneas.\n\n"
        "Por niveles queda así (abajo los más chicos):\n\n```\n"
        + "\n".join(reversed(o.niveles_texto().split("\n")))
        + "\n```\n\n```mermaid\n" + o.mermaid() + "\n```",
    )
    incomp = o.incomparables()
    ej.agregar(
        "a) ¿Total o parcial?",
        (
            f"Es un orden **parcial**: hay elementos incomparables. Por ejemplo "
            f"{o.etiquetas[incomp[0][0]]} y {o.etiquetas[incomp[0][1]]} no están "
            f"relacionados en ningún sentido (no hay camino ascendente de uno al otro). "
            f"Para ser total, **todo** par de elementos debería ser comparable, y el "
            f"diagrama de Hasse sería una única cadena vertical."
            if incomp
            else "Es un orden **total**: todo par de elementos es comparable."
        ),
    )
    conjunto_B = "{" + ", ".join(o.etiquetas[b] for b in B) + "}"
    maxi = o.maximales(B)
    mini = o.minimales(B)
    mx, mn = o.maximo(B), o.minimo(B)
    cs, ci = o.cotas_superiores(B), o.cotas_inferiores(B)
    sup, inf = o.supremo(B), o.infimo(B)

    def nombres(xs):
        return "{" + ", ".join(o.etiquetas[x] for x in xs) + "}" if xs else "∅"

    ej.agregar(
        f"b) Un subconjunto que cumple lo pedido: B = {conjunto_B}",
        f"**Maximales de B**: {nombres(maxi)} — son los elementos de B que no tienen a "
        f"nadie de B por encima.\n\n"
        f"**Minimales de B**: {nombres(mini)} — los que no tienen a nadie de B por debajo.\n\n"
        f"**Máximo de B**: {o.etiquetas[mx] if mx else '**no tiene**'} — el máximo debe ser "
        f"un elemento **de B** que esté por encima de *todos* los demás de B. "
        + (
            f"Acá {o.etiquetas[mx]} cumple eso."
            if mx
            else f"Acá hay {len(maxi)} maximales y son incomparables entre sí, así que "
            f"ninguno está por encima de todos: por eso B **no tiene máximo**. Es la "
            f"diferencia clave entre *maximal* (nadie por encima) y *máximo* (por encima "
            f"de todos)."
        )
        + f"\n\n**Mínimo de B**: {o.etiquetas[mn] if mn else '**no tiene**'}"
        + (f" — está por debajo de todos los elementos de B." if mn else " — por el mismo motivo."),
    )
    ej.agregar(
        "c) Cotas, supremo e ínfimo",
        f"**Cotas superiores de B**: {nombres(cs)} — elementos de **A** (no necesariamente "
        f"de B) que están por encima de todos los de B.\n\n"
        f"**Supremo**: {o.etiquetas[sup] if sup else '**no tiene**'} — es la **menor** de "
        f"las cotas superiores. "
        + (
            "Existe porque el conjunto de cotas superiores tiene mínimo."
            if sup
            else "No existe: el conjunto de cotas superiores está vacío o no tiene mínimo."
        )
        + f"\n\n**Cotas inferiores de B**: {nombres(ci)}\n\n"
        f"**Ínfimo**: {o.etiquetas[inf] if inf else '**no tiene**'} — es la **mayor** de las "
        f"cotas inferiores.",
    )
    ej.respuesta = (
        f"Orden parcial. B = {conjunto_B}: maximales {nombres(maxi)}, minimales "
        f"{nombres(mini)}, máximo {o.etiquetas[mx] if mx else '—'}, mínimo "
        f"{o.etiquetas[mn] if mn else '—'}, supremo {o.etiquetas[sup] if sup else '—'}, "
        f"ínfimo {o.etiquetas[inf] if inf else '—'}."
    )
    ej.observacion = (
        "Las cuatro nociones se confunden todo el tiempo. Máximo y mínimo son **elementos "
        "del subconjunto** y, si existen, son únicos. Maximales y minimales pueden ser "
        "varios. Cotas, supremo e ínfimo se buscan en **todo A**, no sólo en B: el supremo "
        "puede no pertenecer a B. Y si B tiene máximo, ese máximo es también el supremo."
    )
    ej.verificacion = (
        "El orden se construyó por clausura transitiva de un grafo acíclico (por eso es "
        "antisimétrico y transitivo por construcción); el diagrama de Hasse es su reducción "
        "transitiva, y todos los elementos particulares se calcularon recorriendo el orden "
        "completo."
    )
    ej.visual = {
        "tipo": "hasse",
        **serial.orden_a_json(o),
        "particulares": serial.particulares_a_json(o, B),
        "consigna_subconjunto": texto_spec,
    }
    ej.practica = _practica_particulares(o, B)
    return ej


def _practica_particulares(o, B) -> Dict:
    """Elegir máximo, mínimo, supremo e ínfimo del subconjunto.

    «No tiene» es una opción legítima y es justamente la que más se falla: la
    diferencia entre maximal y máximo se juega ahí.
    """
    p = serial.particulares_a_json(o, B)
    etiquetas = dict(o.etiquetas)
    return {
        "tipo": "elementos-particulares",
        "subconjunto": list(B),
        "etiquetas": etiquetas,
        "opciones": list(o.elems),
        "preguntas": [
            {"clave": clave, "texto": texto, "correcta": p[clave]}
            for clave, texto in (
                ("maximo", "Máximo de B"),
                ("minimo", "Mínimo de B"),
                ("supremo", "Supremo de B"),
                ("infimo", "Ínfimo de B"),
            )
        ],
    }


def ej_integrador_partes(rng: random.Random) -> Ejercicio:
    # Se prefiere el caso de tres elementos: P(A) con 8 subconjuntos da un
    # diagrama de Hasse (el cubo) mucho más rico para un ejercicio integrador.
    base = ["a", "b"] if rng.random() < 0.25 else ["a", "b", "c"]
    o = rord.orden_partes(base)
    conjunto = "{" + ", ".join(base) + "}"
    ej = Ejercicio(
        tema="Integrador (Conjuntos + Relaciones)",
        subtema="La inclusión como relación de orden en P(A)",
        consigna=(
            f"Sea A = {conjunto} y sea ≼ la relación definida en P(A) por:\n\n"
            "**X ≼ Y  si y sólo si  X ⊆ Y**\n\n"
            "a) Escribir P(A) por extensión.\n"
            "b) Justificar que ≼ es una relación de orden (reflexiva, antisimétrica y "
            "transitiva) e indicar si es total o parcial.\n"
            "c) Construir el diagrama de Hasse.\n"
            "d) Hallar los elementos particulares de P(A) (máximo, mínimo, maximales, "
            "minimales)."
        ),
        puntaje=20,
    )
    partes = ", ".join(o.etiquetas[e] for e in o.elems)
    ej.agregar(
        "a) El conjunto de partes",
        f"P(A) es el conjunto de **todos** los subconjuntos de A, incluidos ∅ y el propio "
        f"A. Como #A = {len(base)}, hay 2^{len(base)} = {2 ** len(base)} subconjuntos:\n\n"
        f"P(A) = {{ {partes} }}\n\n"
        "Cuidado con la diferencia entre ∈ y ⊆ acá: {" + base[0] + "} **pertenece** a "
        "P(A) y **está incluido** en A. Son dos cosas distintas.",
    )
    ej.agregar(
        "b) Es una relación de orden",
        "**Reflexiva.** Todo conjunto está incluido en sí mismo: X ⊆ X para todo X ∈ P(A), "
        "porque todo elemento de X es elemento de X. ✔\n\n"
        "**Antisimétrica.** Si X ⊆ Y y además Y ⊆ X, entonces X = Y — es exactamente la "
        "definición de igualdad de conjuntos por doble inclusión. ✔\n\n"
        "**Transitiva.** Si X ⊆ Y e Y ⊆ Z, todo elemento de X está en Y, y todo elemento de "
        "Y está en Z; encadenando, todo elemento de X está en Z, o sea X ⊆ Z. ✔\n\n"
        "Al cumplir las tres, ≼ es una **relación de orden amplio**. Es **parcial**, no "
        "total: por ejemplo {" + base[0] + "} y {" + base[1] + "} no son comparables, "
        "porque ninguno está incluido en el otro.",
    )
    ej.agregar(
        "c) Diagrama de Hasse",
        f"Los cubrimientos son: {o.cubrimientos_texto()}\n\n"
        "(cada subconjunto está cubierto por los que se obtienen agregándole **un** "
        "elemento)\n\n"
        "```\n" + "\n".join(reversed(o.niveles_texto().split("\n"))) + "\n```\n\n"
        "```mermaid\n" + o.mermaid() + "\n```\n\n"
        f"El diagrama tiene {len(base) + 1} niveles: en el nivel k están los subconjuntos "
        f"de k elementos.",
    )
    todos = o.elems
    mx, mn = o.maximo(todos), o.minimo(todos)
    ej.agregar(
        "d) Elementos particulares",
        f"**Mínimo: ∅.** Está incluido en cualquier conjunto, así que ∅ ≼ X para todo "
        f"X ∈ P(A).\n\n"
        f"**Máximo: {conjunto}.** Todo subconjunto de A está incluido en A.\n\n"
        f"**Minimales:** sólo ∅ (al haber mínimo, es el único minimal).\n\n"
        f"**Maximales:** sólo {conjunto} (al haber máximo, es el único maximal).\n\n"
        "Este es un buen ejemplo para fijar la relación entre las nociones: **si existe "
        "máximo, entonces es el único maximal**; la recíproca es falsa (puede haber un "
        "único maximal sin que sea máximo, cuando queda algún elemento incomparable).",
    )
    ej.respuesta = (
        f"P(A) tiene {2 ** len(base)} elementos; ≼ es un orden parcial con mínimo ∅ y "
        f"máximo {conjunto}."
    )
    ej.observacion = (
        "Este ejercicio cruza las dos unidades: los **elementos** del conjunto ordenado son "
        "a su vez **conjuntos**. Mantener la distinción entre ∈ y ⊆ es lo que más se "
        "penaliza en el parcial. Y notar que la antisimetría de ⊆ no es un detalle "
        "técnico: es literalmente el método de doble inclusión que se usa para demostrar "
        "igualdades de conjuntos."
    )
    ej.verificacion = (
        "La relación se construyó comparando efectivamente todos los pares de subconjuntos "
        "por inclusión; el diagrama es la reducción transitiva y los elementos particulares "
        "se calcularon sobre el orden completo."
    )
    ej.visual = {
        "tipo": "hasse",
        **serial.orden_a_json(o),
        "particulares": serial.particulares_a_json(o, todos),
        "conjunto_base": base,
    }
    ej.practica = _practica_particulares(o, todos)
    return ej


# ==========================================================================
# FUNCIONES
# ==========================================================================

def ej_funcion_dominio(rng: random.Random) -> Ejercicio:
    d = fdom.generar(rng)
    ej = Ejercicio(
        tema="Funciones",
        subtema="Dominio natural",
        consigna=f"Determinar el dominio natural de la siguiente función:\n\n**{d['texto']}**",
        puntaje=10,
    )
    ej.agregar(
        "Qué significa «dominio natural»",
        "Es el conjunto **más grande** de números reales donde la fórmula tiene sentido. "
        "Hay tres restricciones para buscar, y sólo tres:\n\n"
        "1. **Denominadores**: no pueden valer 0.\n"
        "2. **Raíces de índice par**: el radicando debe ser ≥ 0.\n"
        "3. **Logaritmos**: el argumento debe ser > 0 (estricto).\n\n"
        "Si hay varias, el dominio es la **intersección** de todas las condiciones.",
    )
    for titulo, detalle in d["pasos"]:
        ej.agregar(titulo, detalle)
    ej.respuesta = f"Dom f = **{d['dominio']}**"
    ej.observacion = (
        "Prestar atención a si el extremo entra o no: en una raíz el extremo **sí** entra "
        "(el radicando puede ser 0), pero en un logaritmo **no** (el argumento debe ser "
        "estrictamente positivo). Esa diferencia entre corchete y paréntesis se corrige."
    )
    ej.verificacion = (
        "El dominio se controló evaluando la función en 900 puntos: en cada uno se comprobó "
        "que la fórmula se puede calcular exactamente cuando el punto pertenece al dominio "
        "informado."
    )
    ej.visual = {
        "tipo": "dominio",
        "funcion": d["texto"],
        "dominio": serial.dominio_a_json(d["dominio"]),
        "muestras": serial.muestrear(d["f"], d["dominio"]),
    }
    alternativos = _dominios_alternativos(d["dominio"])
    ej.practica = {
        "tipo": "opcion-multiple",
        "pregunta": f"¿Cuál es el dominio natural de {d['texto']}?",
        **_opciones(str(d["dominio"]), [str(x) for x in alternativos]),
    }
    return ej


def _mismo_conjunto(a, b, muestras: int = 400) -> bool:
    """¿Dos dominios son el mismo conjunto?

    Se muestrea una grilla **y además los extremos exactos**: sin eso no se
    distinguiría [2 ; +∞) de (2 ; +∞), que difieren en un solo punto.
    """
    puntos = [-12 + 24 * i / muestras for i in range(muestras + 1)]
    for dom in (a, b):
        for i in dom.intervalos:
            if i.izq is not None:
                puntos.append(float(i.izq))
            if i.der is not None:
                puntos.append(float(i.der))
        puntos.extend(float(e) for e in dom.excluidos)
    return all(a.contiene(x) == b.contiene(x) for x in puntos)


def _dominios_alternativos(dom):
    """Dominios parecidos pero realmente distintos, para las opciones erróneas.

    Cada candidato corresponde a un error típico: confundir corchete con
    paréntesis, olvidarse de la rama negativa de una cuadrática, o no excluir el
    punto que anula el denominador.
    """
    from .funciones.intervalos import Dominio, Intervalo, reales

    candidatos = [reales()]
    candidatos.append(
        Dominio(
            [
                Intervalo(
                    i.izq,
                    i.der,
                    (not i.izq_cerrado) if i.izq is not None else False,
                    (not i.der_cerrado) if i.der is not None else False,
                )
                for i in dom.intervalos
            ],
            dom.excluidos,
        )
    )
    if len(dom.intervalos) > 1:
        candidatos.append(Dominio([dom.intervalos[-1]], dom.excluidos))
        candidatos.append(Dominio([dom.intervalos[0]], dom.excluidos))
    if dom.excluidos:
        candidatos.append(Dominio(dom.intervalos, []))
        punto = dom.excluidos[0]
        # Excluir el opuesto (error de signo al despejar) y confundir "≠" con ">".
        candidatos.append(Dominio(dom.intervalos, [-punto]))
        candidatos.append(Dominio([Intervalo(punto, None, False, False)]))
    else:
        finitos = [i.izq for i in dom.intervalos if i.izq is not None]
        if finitos:
            candidatos.append(Dominio([Intervalo(None, None, False, False)], [finitos[0]]))
    return [c for c in candidatos if not _mismo_conjunto(c, dom)]


def ej_funcion_biyectiva(rng: random.Random) -> Ejercicio:
    d = fbiy.generar(rng)
    ej = Ejercicio(
        tema="Funciones",
        subtema="Biyectividad y función inversa",
        consigna=(
            f"Dada f : A ⊆ ℝ → ℝ / **{d['texto']}**\n\n"
            "a) Determinar el dominio natural.\n"
            "b) Analizar si es inyectiva y si es sobreyectiva. Justificar.\n"
            "c) Si no es biyectiva, redefinirla para que admita inversa. Escribir f⁻¹."
        ),
        puntaje=15,
    )
    nota_restriccion = (
        "\n\nNo confundir con el dominio **restringido** del inciso c): el natural es el "
        "conjunto más grande donde la fórmula tiene sentido, y acá la fórmula se puede "
        "calcular para cualquier real. La restricción aparece recién cuando se busca la "
        "inversa."
        if str(d["dominio_natural"]) != str(d["dominio"])
        else ""
    )
    ej.agregar(
        "a) Dominio natural", f"Dom f = **{d['dominio_natural']}**" + nota_restriccion
    )
    ej.agregar("b) Inyectividad y sobreyectividad", d["analisis"])
    ej.agregar("c) Redefinición", d["redefinir"])
    ej.agregar(
        "c) Despeje de la inversa",
        "Para hallar f⁻¹ se escribe y = f(x) y se despeja x en función de y; al final se "
        "renombran las variables.\n\n" + d["despeje"] + "\n\n"
        f"Renombrando, **{d['inversa_texto']}**",
    )
    ej.agregar(
        "Control",
        f"El dominio de f⁻¹ es la imagen de f ({d['imagen']}) y su imagen es el dominio de "
        f"f ({d['dominio']}): al invertir una función, dominio e imagen se intercambian. "
        "Gráficamente, f y f⁻¹ son simétricas respecto de la recta y = x.",
    )
    ej.respuesta = (
        f"Dom natural = {d['dominio_natural']} · biyectiva de {d['dominio']} en "
        f"{d['imagen']} · **{d['inversa_texto']}**"
    )
    ej.observacion = (
        "Una función admite inversa **si y sólo si** es biyectiva. Por eso casi siempre hay "
        "que redefinir: restringir el dominio arregla la inyectividad y achicar el "
        "codominio a la imagen arregla la sobreyectividad. Un error típico es dar la "
        "inversa sin aclarar entre qué conjuntos está definida."
    )
    ej.verificacion = (
        "Se comprobó numéricamente que f⁻¹(f(x)) = x en cientos de puntos del dominio y que "
        "f(x) cae siempre dentro de la imagen declarada."
    )
    ej.visual = {
        "tipo": "funcion-inversa",
        "funcion": d["texto"],
        "inversa": d["inversa_texto"],
        "dominio_natural": serial.dominio_a_json(d["dominio_natural"]),
        "dominio": serial.dominio_a_json(d["dominio"]),
        "imagen": serial.dominio_a_json(d["imagen"]),
        "muestras_f": serial.muestrear(d["f"], d["dominio"]),
        # f⁻¹ se muestrea sobre la imagen, que es su dominio.
        "muestras_inversa": serial.muestrear(d["finv"], d["imagen"]),
        "inyectiva": d["inyectiva"],
        "sobreyectiva": d["sobreyectiva"],
    }
    ej.practica = {
        "tipo": "verdadero-falso",
        "items": [
            {"enunciado": "f es inyectiva en su dominio natural",
             "correcta": d["inyectiva"]},
            {"enunciado": "f : Dom f → ℝ es sobreyectiva",
             "correcta": d["sobreyectiva"]},
        ],
    }
    return ej


def ej_funcion_composicion(rng: random.Random) -> Ejercicio:
    d = fcomp.generar(rng)
    ej = Ejercicio(
        tema="Funciones",
        subtema="Composición de funciones",
        consigna=(
            f"Dadas **{d['f_texto']}** y **{d['g_texto']}**, hallar (g ∘ f)(x) y "
            "(f ∘ g)(x), indicando en cada caso el dominio."
        ),
        puntaje=10,
    )
    ej.agregar(
        "Cómo se calcula el dominio de una composición",
        "(g ∘ f)(x) = g(f(x)) se puede calcular cuando pasan **dos** cosas:\n\n"
        "1. x pertenece al dominio de f (para poder calcular f(x)), y\n"
        "2. f(x) pertenece al dominio de g (para poder aplicarle g).\n\n"
        "Las dos condiciones se piden **antes** de simplificar la fórmula final.",
    )
    ej.agregar(
        "(g ∘ f)(x)",
        f"Reemplazando: **{d['gf_texto']}**\n\n{d['gf_razon']}\n\n"
        f"Dom (g ∘ f) = **{d['gf_dominio']}**",
    )
    ej.agregar(
        "(f ∘ g)(x)",
        f"Reemplazando: **{d['fg_texto']}**\n\n{d['fg_razon']}\n\n"
        f"Dom (f ∘ g) = **{d['fg_dominio']}**",
    )
    ej.respuesta = (
        f"{d['gf_texto']} con Dom = {d['gf_dominio']}   |   "
        f"{d['fg_texto']} con Dom = {d['fg_dominio']}"
    )
    ej.observacion = (
        "La composición **no es conmutativa**: g ∘ f y f ∘ g dan fórmulas distintas y, "
        "sobre todo, dominios distintos. Y el dominio no se lee de la fórmula simplificada: "
        "si al simplificar desaparece una raíz o un denominador, la restricción sigue "
        "valiendo igual."
    )
    ej.verificacion = (
        "Ambos dominios se controlaron evaluando g(f(x)) y f(g(x)) en 900 puntos y "
        "comparando con el conjunto informado."
    )
    gf = lambda x: d["g"](d["f"](x))
    fg = lambda x: d["f"](d["g"](x))
    ej.visual = {
        "tipo": "composicion",
        "f": d["f_texto"],
        "g": d["g_texto"],
        "gf": {
            "texto": d["gf_texto"],
            "dominio": serial.dominio_a_json(d["gf_dominio"]),
            "muestras": serial.muestrear(gf, d["gf_dominio"]),
        },
        "fg": {
            "texto": d["fg_texto"],
            "dominio": serial.dominio_a_json(d["fg_dominio"]),
            "muestras": serial.muestrear(fg, d["fg_dominio"]),
        },
    }
    # Emparejar cada composición con su dominio: es el punto exacto donde se
    # falla, porque las dos fórmulas se parecen pero los dominios no.
    ej.practica = {
        "tipo": "emparejar",
        "consigna": "Asociar cada composición con su dominio",
        "izquierda": [d["gf_texto"], d["fg_texto"]],
        "derecha": sorted({str(d["gf_dominio"]), str(d["fg_dominio"])}),
        "correctas": [str(d["gf_dominio"]), str(d["fg_dominio"])],
    }
    return ej


# ==========================================================================
# Armado del examen
# ==========================================================================

GENERADORES: Dict[str, Callable[[random.Random], Ejercicio]] = {
    "simplificacion": ej_simplificacion,
    "derivacion": ej_derivacion,
    "cuantificadores": ej_cuantificadores,
    "conjuntos-extension": ej_conjuntos_extension,
    "venn": ej_venn,
    "identidad": ej_identidad_conjuntos,
    "relacion-propiedades": ej_relacion_propiedades,
    "equivalencia": ej_relacion_equivalencia,
    "orden": ej_relacion_orden,
    "partes-orden": ej_integrador_partes,
    "dominio": ej_funcion_dominio,
    "biyectiva": ej_funcion_biyectiva,
    "composicion": ej_funcion_composicion,
}

TEMAS = {
    "logica": ["simplificacion", "derivacion", "cuantificadores"],
    "conjuntos": ["conjuntos-extension", "venn", "identidad"],
    "relaciones": ["relacion-propiedades", "equivalencia", "orden", "partes-orden"],
    "funciones": ["dominio", "biyectiva", "composicion"],
}

MODOS = {
    # El integrador cubre las cuatro unidades e incluye el ejercicio que las cruza.
    "integrador": [
        "simplificacion",
        "cuantificadores",
        "venn",
        "identidad",
        "partes-orden",
        "biyectiva",
        "composicion",
    ],
    # Formato exacto del primer parcial: Lógica 40 % / Conjuntos 30 % / Relaciones 30 %.
    "parcial1": [
        "simplificacion",
        "derivacion",
        "cuantificadores",
        "conjuntos-extension",
        "identidad",
        "relacion-propiedades",
        "orden",
    ],
    "completo": list(GENERADORES.keys()),
    "express": ["simplificacion", "venn", "relacion-propiedades", "dominio"],
}


def generar_examen(modo: str = "integrador", semilla: int = None, tema: str = None) -> Dict:
    """Arma un examen completo. Devuelve título, semilla y lista de Ejercicios."""
    if semilla is None:
        semilla = random.randrange(1, 10 ** 6)
    rng = random.Random(semilla)

    if tema:
        if tema not in TEMAS:
            raise ValueError(f"Tema desconocido: {tema}. Opciones: {', '.join(TEMAS)}")
        claves = TEMAS[tema]
        titulo = f"Práctica de {tema.capitalize()}"
    else:
        if modo not in MODOS:
            raise ValueError(f"Modo desconocido: {modo}. Opciones: {', '.join(MODOS)}")
        claves = MODOS[modo]
        titulo = {
            "integrador": "Examen Integrador",
            "parcial1": "Simulacro de Primer Parcial",
            "completo": "Práctica completa (todos los tipos de ejercicio)",
            "express": "Práctica exprés",
        }[modo]

    ejercicios = [GENERADORES[c](rng) for c in claves]
    total = sum(e.puntaje for e in ejercicios)
    return {
        "titulo": titulo,
        "modo": tema or modo,
        "semilla": semilla,
        "ejercicios": ejercicios,
        "puntaje_total": total,
    }
