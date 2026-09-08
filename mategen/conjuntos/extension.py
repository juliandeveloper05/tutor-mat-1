"""Determinar conjuntos por extensión a partir de datos (estilo parcial).

Los datos se construyen a partir de conjuntos elegidos al azar, y la resolución
reconstruye los conjuntos con un razonamiento que se puede escribir en el
examen. Al final se verifica que lo reconstruido coincida con lo original.
"""

import random
from typing import Dict, List, Set, Tuple


def _llaves(conjunto) -> str:
    if not conjunto:
        return "∅"
    return "{" + ", ".join(str(x) for x in sorted(conjunto)) + "}"


def _pares(a: Set[int], b: Set[int]) -> str:
    return "{" + ", ".join(f"({x}, {y})" for x in sorted(a) for y in sorted(b)) + "}"


def generar(rng: random.Random) -> Dict:
    """Genera el ejercicio. Devuelve un diccionario con datos y resolución."""
    plantilla = rng.choice(["producto", "uniones"])
    universo = list(range(1, 10))

    if plantilla == "producto":
        # Datos: A×B, C−B y C∩B  (modelo del parcial del 08/10/24)
        a = set(rng.sample(universo, rng.randint(2, 3)))
        b = set(rng.sample([x for x in universo if x not in a], rng.randint(2, 3)))
        c_inter_b = set(rng.sample(sorted(b), rng.randint(1, min(2, len(b)))))
        resto = [x for x in universo if x not in b and x not in c_inter_b]
        c_menos_b = set(rng.sample(resto, rng.randint(1, 3)))
        c = c_inter_b | c_menos_b

        datos = [
            ("A × B", _pares(a, b)),
            ("C − B", _llaves(c_menos_b)),
            ("C ∩ B", _llaves(c_inter_b)),
        ]
        pasos = [
            (
                "Recuperar A y B del producto cartesiano",
                "Por definición, A × B = {(x, y) : x ∈ A ∧ y ∈ B}: **todo** elemento de A se "
                "combina con **todo** elemento de B. Entonces A es el conjunto de las primeras "
                "componentes y B el de las segundas.\n\n"
                f"- Primeras componentes: A = {_llaves(a)}\n"
                f"- Segundas componentes: B = {_llaves(b)}\n\n"
                f"Control: #(A × B) = #A · #B = {len(a)} · {len(b)} = {len(a) * len(b)}, "
                f"y el dato tiene {len(a) * len(b)} pares. ✔",
            ),
            (
                "Reconstruir C",
                "Todo elemento de C está en B o no está en B, y esos dos casos son "
                "excluyentes. Por lo tanto C = (C − B) ∪ (C ∩ B):\n\n"
                f"C = {_llaves(c_menos_b)} ∪ {_llaves(c_inter_b)} = {_llaves(c)}",
            ),
        ]
    else:
        # Datos: A∪B, B∪C, A−B, A∩B, C∩B  (modelo del recuperatorio del 26/11/24)
        a_menos_b = set(rng.sample(universo, rng.randint(1, 2)))
        a_inter_b = set(rng.sample([x for x in universo if x not in a_menos_b], 2))
        resto = [x for x in universo if x not in a_menos_b and x not in a_inter_b]
        b_sola = set(rng.sample(resto, rng.randint(1, 2)))
        resto = [x for x in resto if x not in b_sola]
        c_inter_b = set(rng.sample(sorted(a_inter_b | b_sola), 1))
        c_sola = set(rng.sample(resto, rng.randint(1, 2)))
        a = a_menos_b | a_inter_b
        b = a_inter_b | b_sola
        c = c_inter_b | c_sola

        datos = [
            ("A ∪ B", _llaves(a | b)),
            ("B ∪ C", _llaves(b | c)),
            ("A − B", _llaves(a_menos_b)),
            ("A ∩ B", _llaves(a_inter_b)),
            ("C ∩ B", _llaves(c_inter_b)),
        ]
        pasos = [
            (
                "Reconstruir A",
                "Un elemento de A está en B o no lo está, y no hay otra posibilidad: "
                "A = (A − B) ∪ (A ∩ B).\n\n"
                f"A = {_llaves(a_menos_b)} ∪ {_llaves(a_inter_b)} = {_llaves(a)}",
            ),
            (
                "Reconstruir B",
                "De A ∪ B hay que descartar exactamente los elementos que están en A pero no "
                "en B, es decir A − B: B = (A ∪ B) − (A − B).\n\n"
                f"B = {_llaves(a | b)} − {_llaves(a_menos_b)} = {_llaves(b)}",
            ),
            (
                "Reconstruir C",
                "Igual que antes, separo C según esté o no en B: C = ((B ∪ C) − B) ∪ (C ∩ B). "
                "El primer término aporta los elementos de C que no están en B; el segundo, "
                "los compartidos.\n\n"
                f"C = ({_llaves(b | c)} − {_llaves(b)}) ∪ {_llaves(c_inter_b)} = "
                f"{_llaves((b | c) - b)} ∪ {_llaves(c_inter_b)} = {_llaves(c)}",
            ),
        ]

    regiones = {
        "sólo A": a - b - c,
        "sólo B": b - a - c,
        "sólo C": c - a - b,
        "A ∩ B (sin C)": (a & b) - c,
        "A ∩ C (sin B)": (a & c) - b,
        "B ∩ C (sin A)": (b & c) - a,
        "A ∩ B ∩ C": a & b & c,
    }
    return {
        "plantilla": plantilla,
        "datos": datos,
        "A": a,
        "B": b,
        "C": c,
        "pasos": pasos,
        "regiones": regiones,
        "texto_A": _llaves(a),
        "texto_B": _llaves(b),
        "texto_C": _llaves(c),
    }


def verificar(ej: Dict) -> bool:
    """Comprueba que los datos publicados determinan los conjuntos hallados."""
    a, b, c = ej["A"], ej["B"], ej["C"]
    esperado = dict(ej["datos"])
    if ej["plantilla"] == "producto":
        return (
            esperado["A × B"] == _pares(a, b)
            and esperado["C − B"] == _llaves(c - b)
            and esperado["C ∩ B"] == _llaves(c & b)
        )
    return (
        esperado["A ∪ B"] == _llaves(a | b)
        and esperado["B ∪ C"] == _llaves(b | c)
        and esperado["A − B"] == _llaves(a - b)
        and esperado["A ∩ B"] == _llaves(a & b)
        and esperado["C ∩ B"] == _llaves(c & b)
    )
