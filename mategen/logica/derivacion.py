"""Razonamientos y método de derivaciones.

Se genera un razonamiento a partir de plantillas con la forma de los que toma la
cátedra, y la demostración se *encuentra* con un encadenador hacia adelante que
sólo usa las reglas de inferencia vistas en clase. Si el encadenador no llega a
la conclusión, el razonamiento se descarta: nunca se propone algo sin
demostración. Además la validez se controla con la tabla de verdad.
"""

import random
from typing import Dict, List, Optional, Tuple

from .formula import (
    And,
    Form,
    Imp,
    Not,
    Or,
    Var,
    equivalentes,
    es_tautologia,
    escribir,
)

# Un paso de la derivación: (fórmula, justificación, renglones usados)
Renglon = Tuple[Form, str, List[int]]


def _nuevas(pool: List[Form], meta: Form) -> List[Renglon]:
    """Todas las fórmulas deducibles en un paso a partir de `pool`."""
    salida: List[Renglon] = []
    indice = {f: i for i, f in enumerate(pool)}

    for i, f in enumerate(pool):
        # Simplificación: de una conjunción se deduce cada componente.
        if isinstance(f, And):
            salida.append((f.a, "Simplificación", [i + 1]))
            salida.append((f.b, "Simplificación", [i + 1]))
        # Doble negación
        if isinstance(f, Not) and isinstance(f.a, Not):
            salida.append((f.a.a, "Doble negación", [i + 1]))
        # Ley del condicional: ¬p ∨ q ≡ p → q
        if isinstance(f, Or) and isinstance(f.a, Not):
            salida.append((Imp(f.a.a, f.b), "Ley del condicional", [i + 1]))

        for j, g in enumerate(pool):
            if i == j:
                continue
            if isinstance(f, Imp):
                if g == f.a:  # Modus Ponens
                    salida.append((f.b, "Modus Ponens", [i + 1, j + 1]))
                if g == Not(f.b) or Not(g) == f.b:  # Modus Tollens
                    salida.append((Not(f.a), "Modus Tollens", [i + 1, j + 1]))
                if isinstance(g, Imp) and f.b == g.a:  # Silogismo hipotético
                    salida.append((Imp(f.a, g.b), "Silogismo hipotético", [i + 1, j + 1]))
            if isinstance(f, Or):  # Silogismo disyuntivo
                if g == Not(f.a) or Not(g) == f.a:
                    salida.append((f.b, "Silogismo disyuntivo", [i + 1, j + 1]))
                if g == Not(f.b) or Not(g) == f.b:
                    salida.append((f.a, "Silogismo disyuntivo", [i + 1, j + 1]))

    # Conjunción: sólo si la conjunción sirve de antecedente de alguna premisa
    # o es la meta (evita generar basura combinatoria).
    utiles = {m.a for m in pool if isinstance(m, Imp)}
    utiles.add(meta)
    for i, f in enumerate(pool):
        for j, g in enumerate(pool):
            if i == j:
                continue
            cand = And(f, g)
            if cand in utiles:
                salida.append((cand, "Conjunción", [i + 1, j + 1]))
    return salida


def derivar(premisas: List[Form], meta: Form, max_pasos: int = 10) -> Optional[List[Renglon]]:
    """Busca una derivación de `meta` a partir de `premisas`.

    Devuelve la lista de renglones (premisas incluidas) o None si no encuentra.
    Estrategia: BFS por niveles, quedándose con la primera derivación hallada, y
    después se podan los renglones que no intervienen en la conclusión.
    """
    renglones: List[Renglon] = [(p, "Premisa", []) for p in premisas]
    pool = list(premisas)
    if meta in pool:
        return _podar(renglones, pool.index(meta) + 1)

    for _ in range(max_pasos):
        agregados = False
        for formula, regla, refs in _nuevas(pool, meta):
            if formula in pool:
                continue
            pool.append(formula)
            renglones.append((formula, regla, refs))
            agregados = True
            if formula == meta:
                return _podar(renglones, len(renglones))
            if len(pool) > 220:  # cota de seguridad
                return None
        if not agregados:
            return None
    return None


def _podar(renglones: List[Renglon], final: int) -> List[Renglon]:
    """Deja sólo los renglones de los que depende el renglón `final` y renumera."""
    necesarios = set()
    pendientes = [final]
    while pendientes:
        n = pendientes.pop()
        if n in necesarios:
            continue
        necesarios.add(n)
        pendientes.extend(renglones[n - 1][2])

    orden = sorted(necesarios)
    mapa = {viejo: nuevo + 1 for nuevo, viejo in enumerate(orden)}
    return [
        (renglones[n - 1][0], renglones[n - 1][1], [mapa[r] for r in renglones[n - 1][2]])
        for n in orden
    ]


def es_valido(premisas: List[Form], conclusion: Form) -> bool:
    """Validez semántica: (P1 ∧ ... ∧ Pn) → C debe ser tautología."""
    conjuncion = premisas[0]
    for p in premisas[1:]:
        conjuncion = And(conjuncion, p)
    return es_tautologia(Imp(conjuncion, conclusion))


# --------------------------------------------------------------------------
# Plantillas con la forma de los razonamientos que toma la cátedra
# --------------------------------------------------------------------------

def _plantillas(a: Form, b: Form, c: Form, d: Form, e: Form, f: Form):
    return [
        ([And(a, b), Imp(a, And(c, d)), Imp(d, Or(e, f)), Not(e)], f),
        ([Imp(a, b), Imp(b, And(c, d)), Or(Not(c), Or(Not(e), f)), And(a, e)], f),
        ([Imp(a, b), Or(b, c), Not(b), Imp(c, d)], d),
        ([Imp(a, b), Imp(c, d), Or(a, c), Not(d)], b),
        ([And(a, b), Imp(Or(a, c), d), Imp(d, And(e, f))], f),
        ([Imp(a, Not(b)), And(a, c), Imp(Not(b), Or(d, e)), Not(d)], e),
        ([Or(a, b), Not(a), Imp(b, c), Imp(c, d)], d),
    ]


def generar_derivacion(rng: random.Random) -> Tuple[List[Form], Form, List[Renglon]]:
    """Devuelve (premisas, conclusión, derivación) de un razonamiento válido."""
    nombres = ["p", "q", "r", "s", "t", "u"]
    for _ in range(200):
        mezcla = nombres[:]
        rng.shuffle(mezcla)
        atomos = [Var(n) for n in mezcla]
        premisas, meta = rng.choice(_plantillas(*atomos))
        if not es_valido(premisas, meta):
            continue
        prueba = derivar(premisas, meta)
        if prueba is None or len(prueba) < len(premisas) + 2:
            continue
        return premisas, meta, prueba
    raise RuntimeError("No se pudo generar el razonamiento")


def formatear(prueba: List[Renglon]) -> str:
    """Derivación numerada, como se escribe en el parcial."""
    lineas = []
    for i, (formula, regla, refs) in enumerate(prueba, start=1):
        just = regla if not refs else f"{regla} " + (
            f"en {refs[0]}" if len(refs) == 1 else f"entre {refs[0]} y {refs[1]}"
        )
        lineas.append(f"| {i} | {escribir(formula)} | {just} |")
    return "\n".join(
        ["| # | Fórmula | Justificación |", "|---|---|---|"] + lineas
    )


def verificar_derivacion(prueba: List[Renglon], premisas: List[Form], meta: Form) -> bool:
    """Control independiente de la derivación, renglón por renglón.

    No mira qué regla dice haber usado: comprueba semánticamente que cada
    renglón se sigue de los renglones que cita (la implicación tiene que ser una
    tautología). Así, una regla mal implementada quedaría en evidencia.
    """
    if not prueba or prueba[-1][0] != meta:
        return False
    for i, (formula, regla, refs) in enumerate(prueba):
        if regla == "Premisa":
            if formula not in premisas or refs:
                return False
            continue
        if not refs or any(r < 1 or r > i for r in refs):
            return False  # sólo puede citar renglones anteriores
        soporte = prueba[refs[0] - 1][0]
        for r in refs[1:]:
            soporte = And(soporte, prueba[r - 1][0])
        if not es_tautologia(Imp(soporte, formula)):
            return False
    return True
