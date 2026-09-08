"""Ayudas para escribir expresiones algebraicas como las escribe una persona.

Sin esto salen cosas como "x − −3", "1x", "(x − 3) / 1" o "0 + ln(x)", que en un
material de estudio distraen y dan desconfianza.
"""

from fractions import Fraction

from .intervalos import num


def desplazar(var: str, h) -> str:
    """x − h, escrito bien para h positivo, negativo o cero."""
    h = Fraction(h)
    if h == 0:
        return var
    return f"{var} − {num(h)}" if h > 0 else f"{var} + {num(-h)}"


def sumar(expr: str, k) -> str:
    """expr + k."""
    k = Fraction(k)
    if k == 0:
        return expr
    return f"{expr} + {num(k)}" if k > 0 else f"{expr} − {num(-k)}"


def coef(a, expr: str) -> str:
    """a·expr, omitiendo el 1."""
    a = Fraction(a)
    if a == 1:
        return expr
    if a == -1:
        return f"−{expr}"
    return f"{num(a)}{expr}"


def parentizar(expr: str) -> str:
    """Agrega paréntesis sólo si hacen falta."""
    if " " not in expr:
        return expr
    return f"({expr})"


def dividir(expr: str, d) -> str:
    """expr / d, omitiendo la división por 1 y parentizando el numerador."""
    d = Fraction(d)
    if d == 1:
        return expr
    return f"{parentizar(expr)} / {num(d)}"


def anteponer(h, expr: str) -> str:
    """h + expr, omitiendo el 0."""
    h = Fraction(h)
    if h == 0:
        return expr
    return f"{num(h)} + {expr}" if h > 0 else f"{expr} − {num(-h)}"
