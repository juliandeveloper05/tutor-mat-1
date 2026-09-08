"""Conjuntos de números reales expresados como unión de intervalos.

Se usan fracciones exactas para que los extremos queden escritos como −3/2 y no
como −1.5, que es lo que se espera en el examen.
"""

from fractions import Fraction
from typing import List, Optional, Tuple

INF = None  # representa ±∞


def num(x: Fraction) -> str:
    """Escribe una fracción como la escribiría una persona."""
    f = Fraction(x)
    texto = str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"
    return texto.replace("-", "−")  # signo menos tipográfico, como en el apunte


class Intervalo:
    def __init__(self, izq, der, izq_cerrado: bool, der_cerrado: bool):
        self.izq = izq if izq is None else Fraction(izq)
        self.der = der if der is None else Fraction(der)
        self.izq_cerrado = izq_cerrado and izq is not None
        self.der_cerrado = der_cerrado and der is not None

    def __str__(self) -> str:
        a = "−∞" if self.izq is None else num(self.izq)
        b = "+∞" if self.der is None else num(self.der)
        return ("[" if self.izq_cerrado else "(") + a + " ; " + b + ("]" if self.der_cerrado else ")")

    def contiene(self, x: float) -> bool:
        if self.izq is not None:
            if x < float(self.izq) or (x == float(self.izq) and not self.izq_cerrado):
                return False
        if self.der is not None:
            if x > float(self.der) or (x == float(self.der) and not self.der_cerrado):
                return False
        return True


class Dominio:
    """Unión de intervalos, opcionalmente con puntos excluidos."""

    def __init__(self, intervalos: List[Intervalo], excluidos: Optional[List[Fraction]] = None):
        self.intervalos = intervalos
        self.excluidos = [Fraction(e) for e in (excluidos or [])]

    def __str__(self) -> str:
        # ℝ y ℝ − {…} se escriben así, no como (−∞ ; +∞).
        if len(self.intervalos) == 1:
            i = self.intervalos[0]
            if i.izq is None and i.der is None:
                if not self.excluidos:
                    return "ℝ"
                return "ℝ − {" + ", ".join(num(e) for e in self.excluidos) + "}"
        base = " ∪ ".join(str(i) for i in self.intervalos)
        if self.excluidos:
            base += " − {" + ", ".join(num(e) for e in self.excluidos) + "}"
        return base

    def contiene(self, x: float) -> bool:
        if any(abs(x - float(e)) < 1e-12 for e in self.excluidos):
            return False
        return any(i.contiene(x) for i in self.intervalos)


def reales() -> Dominio:
    return Dominio([Intervalo(None, None, False, False)])


def desde(a, cerrado: bool = True) -> Dominio:
    return Dominio([Intervalo(a, None, cerrado, False)])


def hasta(a, cerrado: bool = True) -> Dominio:
    return Dominio([Intervalo(None, a, False, cerrado)])


def reales_sin(puntos) -> Dominio:
    return Dominio([Intervalo(None, None, False, False)], list(puntos))
