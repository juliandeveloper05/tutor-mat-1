"""Relaciones de orden: diagrama de Hasse y elementos particulares."""

import random
from itertools import combinations
from typing import Dict, List, Optional, Set, Tuple

Par = Tuple[str, str]


def clausura_transitiva(elems: List[str], aristas: Set[Par]) -> Set[Par]:
    R = set(aristas)
    cambio = True
    while cambio:
        cambio = False
        for (x, y) in list(R):
            for (u, z) in list(R):
                if y == u and (x, z) not in R:
                    R.add((x, z))
                    cambio = True
    return R


def reduccion_transitiva(elems: List[str], estricto: Set[Par]) -> Set[Par]:
    """Aristas del diagrama de Hasse: las relaciones de cubrimiento."""
    hasse = set()
    for (x, y) in estricto:
        intermedio = any(
            (x, z) in estricto and (z, y) in estricto for z in elems if z not in (x, y)
        )
        if not intermedio:
            hasse.add((x, y))
    return hasse


def niveles(elems: List[str], hasse: Set[Par]) -> List[List[str]]:
    """Agrupa los elementos por altura, para dibujar el diagrama."""
    altura: Dict[str, int] = {}

    def calcular(x: str) -> int:
        if x in altura:
            return altura[x]
        debajo = [a for (a, b) in hasse if b == x]
        altura[x] = 0 if not debajo else 1 + max(calcular(a) for a in debajo)
        return altura[x]

    for e in elems:
        calcular(e)
    maximo = max(altura.values())
    return [sorted(e for e in elems if altura[e] == n) for n in range(maximo + 1)]


class Orden:
    def __init__(self, elems: List[str], estricto: Set[Par], etiquetas: Optional[Dict[str, str]] = None):
        self.elems = elems
        # Etiqueta visible de cada elemento (para órdenes de subconjuntos).
        self.etiquetas = etiquetas or {e: e for e in elems}
        self.estricto = estricto                       # x < y
        self.relacion = estricto | {(x, x) for x in elems}   # x ≼ y
        self.hasse = reduccion_transitiva(elems, estricto)

    def precede(self, x: str, y: str) -> bool:
        return (x, y) in self.relacion

    def es_total(self) -> bool:
        return all(
            self.precede(x, y) or self.precede(y, x)
            for x in self.elems
            for y in self.elems
        )

    def incomparables(self) -> List[Par]:
        return [
            (x, y)
            for x, y in combinations(self.elems, 2)
            if not self.precede(x, y) and not self.precede(y, x)
        ]

    # -- elementos particulares de un subconjunto ---------------------------
    def maximales(self, B: List[str]) -> List[str]:
        return sorted(x for x in B if not any(y != x and self.precede(x, y) for y in B))

    def minimales(self, B: List[str]) -> List[str]:
        return sorted(x for x in B if not any(y != x and self.precede(y, x) for y in B))

    def maximo(self, B: List[str]) -> Optional[str]:
        for x in B:
            if all(self.precede(y, x) for y in B):
                return x
        return None

    def minimo(self, B: List[str]) -> Optional[str]:
        for x in B:
            if all(self.precede(x, y) for y in B):
                return x
        return None

    def cotas_superiores(self, B: List[str]) -> List[str]:
        return sorted(x for x in self.elems if all(self.precede(b, x) for b in B))

    def cotas_inferiores(self, B: List[str]) -> List[str]:
        return sorted(x for x in self.elems if all(self.precede(x, b) for b in B))

    def supremo(self, B: List[str]) -> Optional[str]:
        cotas = self.cotas_superiores(B)
        return self.minimo(cotas) if cotas else None

    def infimo(self, B: List[str]) -> Optional[str]:
        cotas = self.cotas_inferiores(B)
        return self.maximo(cotas) if cotas else None

    # -- dibujo -------------------------------------------------------------
    def mermaid(self) -> str:
        """Diagrama de Hasse. Los ids son seguros; la etiqueta va entre corchetes."""
        ids = {e: f"n{i}" for i, e in enumerate(self.elems)}
        lineas = ["graph BT"]
        for e in self.elems:
            lineas.append(f'    {ids[e]}["{self.etiquetas[e]}"]')
        for (x, y) in sorted(self.hasse):
            lineas.append(f"    {ids[y]} --- {ids[x]}")
        return "\n".join(lineas)

    def cubrimientos_texto(self) -> str:
        """Relaciones de cubrimiento: x ≺ y significa que y está justo encima de x."""
        return ",  ".join(
            f"{self.etiquetas[x]} ≺ {self.etiquetas[y]}" for (x, y) in sorted(self.hasse)
        )

    def niveles_texto(self) -> str:
        capas = niveles(self.elems, self.hasse)
        return "\n".join(
            f"    nivel {i}: " + "   ".join(self.etiquetas[e] for e in capa)
            for i, capa in enumerate(capas)
        )


def generar_orden(rng: random.Random, n: int = 6) -> Orden:
    elems = [chr(ord("a") + i) for i in range(n)]
    for _ in range(400):
        orden_lineal = elems[:]
        rng.shuffle(orden_lineal)
        aristas = set()
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < 0.35:
                    aristas.add((orden_lineal[i], orden_lineal[j]))
        estricto = clausura_transitiva(elems, aristas)
        o = Orden(elems, estricto)
        if o.es_total():
            continue
        if not (4 <= len(o.hasse) <= 8):
            continue
        if len(o.maximales(elems)) < 2 and len(o.minimales(elems)) < 2:
            continue
        if len(niveles(elems, o.hasse)) < 3:
            continue
        return o
    raise RuntimeError("No se pudo generar el orden")


def buscar_subconjunto(o: Orden, rng: random.Random, tam: int, spec: Dict) -> Optional[List[str]]:
    """Busca un subconjunto de `tam` elementos que cumpla las condiciones pedidas."""
    candidatos = []
    for B in combinations(o.elems, tam):
        B = list(B)
        if "con_maximo" in spec and (o.maximo(B) is not None) != spec["con_maximo"]:
            continue
        if "con_minimo" in spec and (o.minimo(B) is not None) != spec["con_minimo"]:
            continue
        if "maximales" in spec and len(o.maximales(B)) != spec["maximales"]:
            continue
        if "minimales" in spec and len(o.minimales(B)) != spec["minimales"]:
            continue
        if "cotas_sup" in spec and len(o.cotas_superiores(B)) != spec["cotas_sup"]:
            continue
        candidatos.append(B)
    return rng.choice(candidatos) if candidatos else None


def orden_partes(base: List[str]) -> Orden:
    """El conjunto de partes de `base` ordenado por inclusión (⊆).

    Es el ejercicio que cruza Conjuntos y Relaciones: los elementos del conjunto
    ordenado son, a su vez, conjuntos.
    """
    from itertools import chain, combinations

    subconjuntos = list(
        chain.from_iterable(combinations(base, r) for r in range(len(base) + 1))
    )
    claves = [f"s{i}" for i in range(len(subconjuntos))]
    etiquetas = {}
    for clave, sub in zip(claves, subconjuntos):
        etiquetas[clave] = "∅" if not sub else "{" + ", ".join(sub) + "}"
    conjuntos = {clave: set(sub) for clave, sub in zip(claves, subconjuntos)}
    estricto = {
        (x, y)
        for x in claves
        for y in claves
        if x != y and conjuntos[x] < conjuntos[y]
    }
    return Orden(claves, estricto, etiquetas)
