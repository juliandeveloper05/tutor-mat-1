"""Problemas de conteo con tres conjuntos (diagrama de Venn).

Se eligen primero las siete regiones del diagrama y recién después se redactan
los datos, de modo que el enunciado siempre es consistente y tiene solución
única. La resolución deduce las regiones en un orden que se puede reproducir a
mano en el parcial.
"""

import random
from typing import Dict, List

CONTEXTOS = [
    {
        "unidad": "comercios",
        "elementos": ("Bloque", "Tofin", "Milki"),
        "letras": ("B", "T", "M"),
        "intro": (
            "Se hace un estudio en {total} comercios, viendo en cuáles se venden las marcas "
            "de chocolate «Bloque», «Tofin» y «Milki»."
        ),
        "pertenece": "se vende «{x}»",
        "pertenece_pl": "se venden «{x}» y «{y}»",
        "las_tres": "se venden las tres marcas",
        "solo": "se vende «{x}» y ninguna de las otras dos",
        "ninguna": "no se vende ninguna de las tres marcas",
        "letra_conjuntos": "Si llamamos B, T y M a los conjuntos de comercios que venden «Bloque», «Tofin» y «Milki» respectivamente",
        "exactamente_una": "se vende exactamente una de estas tres marcas",
    },
    {
        "unidad": "estudiantes",
        "elementos": ("Inglés", "Bases de Datos", "Matemática I"),
        "letras": ("I", "D", "M"),
        "intro": (
            "En un grupo de {total} estudiantes se relevó la inscripción a Inglés, "
            "Bases de Datos y Matemática I."
        ),
        "pertenece": "está inscripto en {x}",
        "pertenece_pl": "están inscriptos en {x} y {y}",
        "las_tres": "están inscriptos en las tres materias",
        "solo": "cursa {x} y ninguna de las otras dos",
        "ninguna": "no está inscripto en ninguna de las tres",
        "letra_conjuntos": "Si llamamos I, D y M a los conjuntos de estudiantes inscriptos en Inglés, Bases de Datos y Matemática I respectivamente",
        "exactamente_una": "se cursa exactamente una de estas tres materias",
    },
    {
        "unidad": "desarrolladores",
        "elementos": ("Python", "Java", "SQL"),
        "letras": ("P", "J", "S"),
        "intro": (
            "En una empresa de software se encuestó a {total} desarrolladores sobre qué "
            "lenguajes usan: Python, Java y SQL."
        ),
        "pertenece": "usa {x}",
        "pertenece_pl": "usan {x} y {y}",
        "las_tres": "usan los tres lenguajes",
        "solo": "usa {x} y ninguno de los otros dos",
        "ninguna": "no usa ninguno de los tres",
        "letra_conjuntos": "Si llamamos P, J y S a los conjuntos de desarrolladores que usan Python, Java y SQL respectivamente",
        "exactamente_una": "se usa exactamente uno de estos tres lenguajes",
    },
]


def generar(rng: random.Random) -> Dict:
    ctx = rng.choice(CONTEXTOS)
    x, y, z = ctx["elementos"]
    LA, LB, LC = ctx["letras"]

    # Las siete regiones del diagrama, más los que quedan afuera.
    abc = rng.randint(4, 12)
    ab = rng.randint(3, 12)
    ac = rng.randint(3, 12)
    bc = rng.randint(3, 12)
    solo_a = rng.randint(8, 22)
    solo_b = rng.randint(8, 22)
    solo_c = rng.randint(8, 22)
    ninguna = rng.randint(1, 6)
    total = abc + ab + ac + bc + solo_a + solo_b + solo_c + ninguna

    card_a = solo_a + ab + ac + abc
    card_b = solo_b + ab + bc + abc
    card_bc = bc + abc
    card_ab = ab + abc

    datos = [
        f"en {abc} {ctx['unidad']} {ctx['las_tres']}",
        f"en {card_ab} " + ctx["pertenece_pl"].format(x=x, y=y),
        f"en {card_a} " + ctx["pertenece"].format(x=x),
        f"en {solo_a} " + ctx["solo"].format(x=x),
        f"en {card_b} " + ctx["pertenece"].format(x=y),
        f"en {card_bc} " + ctx["pertenece_pl"].format(x=y, y=z),
        f"en {ninguna} {ctx['ninguna']}",
    ]

    exactamente_una = solo_a + solo_b + solo_c
    b_no_c = solo_b + ab
    simetrica = (solo_a + ac) + (solo_b + bc)

    pasos = [
        (
            "Nombrar las regiones",
            f"El diagrama de tres conjuntos tiene 8 regiones disjuntas: las 7 de adentro más "
            f"la de afuera. Llamo:\n\n"
            f"- `{LA}{LB}{LC}` = los que están en los tres\n"
            f"- `{LA}{LB}`, `{LA}{LC}`, `{LB}{LC}` = los que están en exactamente esos dos\n"
            f"- `{LA}`, `{LB}`, `{LC}` = los que están en uno solo\n"
            f"- `afuera` = los que no están en ninguno\n\n"
            "La clave del método es **empezar por el centro** y avanzar hacia afuera: cada "
            "dato del tipo «#(X ∩ Y)» incluye a los del centro, así que hay que restarlos.",
        ),
        (
            "Del centro hacia afuera",
            f"1. `{LA}{LB}{LC}` = {abc} (dato directo).\n"
            f"2. `{LA}{LB}` = #({LA} ∩ {LB}) − `{LA}{LB}{LC}` = {card_ab} − {abc} = **{ab}**.\n"
            f"3. `{LA}` = {solo_a} (dato directo: sólo {x}).\n"
            f"4. `{LA}{LC}` = #{LA} − `{LA}` − `{LA}{LB}` − `{LA}{LB}{LC}` = "
            f"{card_a} − {solo_a} − {ab} − {abc} = **{ac}**.\n"
            f"5. `{LB}{LC}` = #({LB} ∩ {LC}) − `{LA}{LB}{LC}` = {card_bc} − {abc} = **{bc}**.\n"
            f"6. `{LB}` = #{LB} − `{LA}{LB}` − `{LB}{LC}` − `{LA}{LB}{LC}` = "
            f"{card_b} − {ab} − {bc} − {abc} = **{solo_b}**.\n"
            f"7. `{LC}` = total − afuera − (todas las anteriores) = "
            f"{total} − {ninguna} − {abc + ab + ac + bc + solo_a + solo_b} = **{solo_c}**.",
        ),
        (
            "Control de consistencia",
            f"La suma de las 8 regiones debe dar el total:\n\n"
            f"{solo_a} + {solo_b} + {solo_c} + {ab} + {ac} + {bc} + {abc} + {ninguna} = "
            f"**{total}** ✔",
        ),
    ]

    preguntas = [
        {
            "texto": f"¿En cuántos {ctx['unidad']} {ctx['exactamente_una']}? "
            f"Escribir además una expresión de conjuntos que represente la respuesta.",
            "expresion": f"({LA} − ({LB} ∪ {LC})) ∪ ({LB} − ({LA} ∪ {LC})) ∪ ({LC} − ({LA} ∪ {LB}))",
            "cuenta": f"`{LA}` + `{LB}` + `{LC}` = {solo_a} + {solo_b} + {solo_c}",
            "valor": exactamente_una,
        },
        {
            "texto": f"¿En cuántos se cumple «{y}» pero no «{z}»?",
            "expresion": f"{LB} − {LC}",
            "cuenta": f"`{LB}` + `{LA}{LB}` = {solo_b} + {ab}",
            "valor": b_no_c,
        },
        {
            "texto": f"¿Cuántos {ctx['unidad']} pertenecen a {LA} △ {LB}? "
            f"Describir ese conjunto en lenguaje cotidiano.",
            "expresion": f"{LA} △ {LB} = ({LA} − {LB}) ∪ ({LB} − {LA})",
            "cuenta": f"(`{LA}` + `{LA}{LC}`) + (`{LB}` + `{LB}{LC}`) = "
            f"({solo_a} + {ac}) + ({solo_b} + {bc})",
            "valor": simetrica,
            "descripcion": f"son los que cumplen exactamente una de las dos condiciones «{x}» o «{y}», "
            f"pero no las dos a la vez (sin importar qué pase con «{z}»)",
        },
    ]

    return {
        "contexto": ctx,
        "intro": ctx["intro"].format(total=total),
        "datos": datos,
        "total": total,
        "regiones": {
            "abc": abc, "ab": ab, "ac": ac, "bc": bc,
            "a": solo_a, "b": solo_b, "c": solo_c, "afuera": ninguna,
        },
        "pasos": pasos,
        "preguntas": preguntas,
    }


def verificar(ej: Dict) -> bool:
    r = ej["regiones"]
    suma = sum(r.values())
    p = ej["preguntas"]
    return (
        suma == ej["total"]
        and p[0]["valor"] == r["a"] + r["b"] + r["c"]
        and p[1]["valor"] == r["b"] + r["ab"]
        and p[2]["valor"] == r["a"] + r["ac"] + r["b"] + r["bc"]
    )
