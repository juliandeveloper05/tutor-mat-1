"""Propiedades de una relación binaria y cómo corregirla.

Todas las conclusiones se acompañan del par que las justifica: si la relación no
es transitiva, el programa dice exactamente qué par falta; si no es
antisimétrica, cuál es el par simétrico que la rompe. Eso es lo que la cátedra
pide como justificación.
"""

import random
from typing import Dict, List, Set, Tuple

Par = Tuple[str, str]


def par(p: Par) -> str:
    return f"({p[0]}, {p[1]})"


def lista(pares) -> str:
    if not pares:
        return "∅"
    return "{" + ", ".join(par(p) for p in sorted(pares)) + "}"


def analizar(A: List[str], R: Set[Par]) -> Dict:
    """Devuelve, para cada propiedad, si se cumple y su testigo/contraejemplo."""
    faltan_diagonal = [(x, x) for x in A if (x, x) not in R]
    hay_diagonal = [(x, x) for x in A if (x, x) in R]
    fallan_simetria = [(x, y) for (x, y) in sorted(R) if (y, x) not in R]
    fallan_antisimetria = [
        (x, y) for (x, y) in sorted(R) if x != y and (y, x) in R and x < y
    ]
    fallan_transitiva = [
        ((x, y), (y, z), (x, z))
        for (x, y) in sorted(R)
        for (u, z) in sorted(R)
        if u == y and (x, z) not in R
    ]
    return {
        "reflexiva": (not faltan_diagonal, faltan_diagonal),
        "irreflexiva": (not hay_diagonal, hay_diagonal),
        "simetrica": (not fallan_simetria, fallan_simetria),
        "antisimetrica": (not fallan_antisimetria, fallan_antisimetria),
        "transitiva": (not fallan_transitiva, fallan_transitiva),
    }


def texto_analisis(A: List[str], R: Set[Par]) -> str:
    an = analizar(A, R)
    lineas = []

    ok, faltan = an["reflexiva"]
    if ok:
        lineas.append(
            "- **Reflexiva: SÍ.** Están todos los pares (x, x) con x ∈ A: "
            + lista([(x, x) for x in A])
            + "."
        )
    else:
        lineas.append(
            f"- **Reflexiva: NO.** Falta {par(faltan[0])} "
            f"(para ser reflexiva hacen falta *todos* los pares de la diagonal; faltan "
            f"{lista(faltan)})."
        )

    ok, hay = an["irreflexiva"]
    if ok:
        lineas.append(
            "- **Irreflexiva (arreflexiva): SÍ.** No hay ningún par de la forma (x, x)."
        )
    else:
        lineas.append(
            f"- **Irreflexiva: NO.** Aparece {par(hay[0])}, que es de la forma (x, x)."
        )

    ok, fallan = an["simetrica"]
    if ok:
        lineas.append(
            "- **Simétrica: SÍ.** Para cada par (x, y) de la relación también está (y, x)."
        )
    else:
        x, y = fallan[0]
        lineas.append(
            f"- **Simétrica: NO.** Está {par((x, y))} pero falta {par((y, x))}."
        )

    ok, fallan = an["antisimetrica"]
    if ok:
        lineas.append(
            "- **Antisimétrica: SÍ.** No hay dos elementos distintos relacionados en ambos "
            "sentidos (los pares (x, x) no afectan la antisimetría)."
        )
    else:
        x, y = fallan[0]
        lineas.append(
            f"- **Antisimétrica: NO.** Están {par((x, y))} y {par((y, x))} con x ≠ y."
        )

    ok, fallan = an["transitiva"]
    if ok:
        lineas.append(
            "- **Transitiva: SÍ.** Cada vez que están (x, y) e (y, z), también está (x, z)."
        )
    else:
        (p1, p2, falta) = fallan[0]
        lineas.append(
            f"- **Transitiva: NO.** Están {par(p1)} y {par(p2)}, pero falta {par(falta)}."
        )
    return "\n".join(lineas)


def hacer_reflexiva(A: List[str], R: Set[Par]) -> List[Par]:
    """Pares mínimos a agregar para que sea reflexiva."""
    return [(x, x) for x in A if (x, x) not in R]


def hacer_irreflexiva(A: List[str], R: Set[Par]) -> List[Par]:
    return [(x, x) for x in A if (x, x) in R]


def hacer_simetrica(A: List[str], R: Set[Par]) -> List[Par]:
    return sorted({(y, x) for (x, y) in R if (y, x) not in R})


def hacer_antisimetrica(A: List[str], R: Set[Par]) -> List[Par]:
    """Pares a quitar (uno por cada par simétrico con elementos distintos)."""
    quitar = []
    for (x, y) in sorted(R):
        if x != y and (y, x) in R and x < y:
            quitar.append((x, y))
    return quitar


def generar(rng: random.Random) -> Dict:
    """Genera una relación con las condiciones que pide el parcial."""
    A = ["a", "b", "c", "d"]
    todos = [(x, y) for x in A for y in A]
    for _ in range(500):
        R = set(rng.sample(todos, rng.randint(4, 7)))
        an = analizar(A, R)
        # Que el ejercicio tenga jugo: que falle la reflexividad (para poder
        # pedir agregar pares) y que haya a lo sumo 2 pares simétricos a quitar.
        if an["reflexiva"][0]:
            continue
        simetricos = hacer_antisimetrica(A, R)
        if not (1 <= len(simetricos) <= 2):
            continue
        if len(hacer_reflexiva(A, R)) > 3:
            continue
        return {
            "A": A,
            "R": R,
            "texto_R": lista(R),
            "analisis": texto_analisis(A, R),
            "agregar_reflexiva": hacer_reflexiva(A, R),
            "quitar_antisimetrica": simetricos,
            "agregar_simetrica": hacer_simetrica(A, R),
            "quitar_irreflexiva": hacer_irreflexiva(A, R),
        }
    raise RuntimeError("No se pudo generar la relación")
