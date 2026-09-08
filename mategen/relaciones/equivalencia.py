"""Relaciones de equivalencia, clases y conjunto cociente."""

import random
from typing import Dict, List, Set, Tuple

from .propiedades import analizar, lista

Par = Tuple[str, str]


def desde_particion(particion: List[List[str]]) -> Set[Par]:
    """La relación de equivalencia asociada a una partición."""
    R: Set[Par] = set()
    for bloque in particion:
        for x in bloque:
            for y in bloque:
                R.add((x, y))
    return R


def clases(A: List[str], R: Set[Par]) -> Dict[str, List[str]]:
    """Clase de equivalencia de cada elemento (asume que R es de equivalencia)."""
    return {x: sorted(y for y in A if (x, y) in R) for x in A}


def cociente(A: List[str], R: Set[Par]) -> List[List[str]]:
    vistos: Set[str] = set()
    salida: List[List[str]] = []
    for x in A:
        if x in vistos:
            continue
        clase = sorted(y for y in A if (x, y) in R)
        vistos.update(clase)
        salida.append(clase)
    return salida


def texto_clase(elemento: str, clase: List[str]) -> str:
    return f"K({elemento}) = " + "{" + ", ".join(clase) + "}"


def generar(rng: random.Random) -> Dict:
    """Genera una relación en un conjunto chico: puede ser de equivalencia o no."""
    A = ["a", "b", "c", "d", "e"]
    for _ in range(300):
        # Partición al azar en 2 o 3 bloques
        elementos = A[:]
        rng.shuffle(elementos)
        cortes = sorted(rng.sample(range(1, len(A)), rng.choice([1, 2])))
        bloques, anterior = [], 0
        for c in cortes + [len(A)]:
            bloques.append(sorted(elementos[anterior:c]))
            anterior = c
        if any(len(b) == 0 for b in bloques):
            continue

        R = desde_particion(bloques)
        es_equivalencia = rng.random() < 0.6
        roto = None
        if not es_equivalencia:
            # Se rompe exactamente una propiedad, para que el ejercicio tenga
            # una respuesta clara.
            opcion = rng.choice(["reflexiva", "simetrica"])
            if opcion == "reflexiva":
                x = rng.choice(A)
                R = R - {(x, x)}
                roto = "reflexiva"
            else:
                candidatos = [(x, y) for (x, y) in R if x != y]
                if not candidatos:
                    continue
                x, y = rng.choice(candidatos)
                R = R - {(x, y)}
                roto = "simetrica"

        an = analizar(A, R)
        realmente = an["reflexiva"][0] and an["simetrica"][0] and an["transitiva"][0]
        if realmente != es_equivalencia:
            continue

        datos = {
            "A": A,
            "R": R,
            "texto_R": lista(R),
            "es_equivalencia": realmente,
            "analisis": an,
            "particion": sorted(bloques, key=lambda b: b[0]),
            "propiedad_rota": roto,
        }
        if realmente:
            datos["clases"] = clases(A, R)
            datos["cociente"] = cociente(A, R)
        return datos
    raise RuntimeError("No se pudo generar la relación de equivalencia")


def verificar(datos: Dict) -> bool:
    A, R = datos["A"], datos["R"]
    an = analizar(A, R)
    es = an["reflexiva"][0] and an["simetrica"][0] and an["transitiva"][0]
    if es != datos["es_equivalencia"]:
        return False
    if not es:
        return True
    # El cociente debe ser una partición de A.
    bloques = datos["cociente"]
    union: Set[str] = set()
    for b in bloques:
        if union & set(b):
            return False
        union |= set(b)
    return union == set(A)
