"""AST de fórmulas proposicionales, tablas de verdad y equivalencia.

Notación usada (la del apunte de la cátedra):
    ¬   negación        ∧   conjunción      ∨   disyunción
    →   condicional     ↔   bicondicional   V/F constantes
"""

from dataclasses import dataclass
from itertools import product
from typing import Dict, List, Tuple


class Form:
    """Clase base de todas las fórmulas."""

    def __str__(self) -> str:  # pragma: no cover - delega en escribir()
        return escribir(self)


@dataclass(frozen=True)
class Var(Form):
    nombre: str


@dataclass(frozen=True)
class Const(Form):
    valor: bool


@dataclass(frozen=True)
class Not(Form):
    a: Form


@dataclass(frozen=True)
class And(Form):
    a: Form
    b: Form


@dataclass(frozen=True)
class Or(Form):
    a: Form
    b: Form


@dataclass(frozen=True)
class Imp(Form):
    a: Form
    b: Form


@dataclass(frozen=True)
class Iff(Form):
    a: Form
    b: Form


# --------------------------------------------------------------------------
# Impresión
# --------------------------------------------------------------------------

_PREC = {Iff: 1, Imp: 2, Or: 3, And: 4, Not: 5}
_SIMB = {And: " ∧ ", Or: " ∨ ", Imp: " → ", Iff: " ↔ "}


def _prec(f: Form) -> int:
    return _PREC.get(type(f), 6)


def escribir(f: Form) -> str:
    """Devuelve la fórmula como texto, con el mínimo de paréntesis necesario."""
    if isinstance(f, Var):
        return f.nombre
    if isinstance(f, Const):
        return "V" if f.valor else "F"
    if isinstance(f, Not):
        interno = escribir(f.a)
        if _prec(f.a) < _prec(f):
            interno = "(" + interno + ")"
        return "¬" + interno
    # Binarias. Criterio de la cátedra: se parentiza toda subfórmula binaria,
    # salvo cadenas del mismo conectivo asociativo (p ∧ q ∧ r).
    izq, der = escribir(f.a), escribir(f.b)
    mismo_asociativo = isinstance(f, (And, Or)) and type(f.a) is type(f)
    if _prec(f.a) < 5 and not mismo_asociativo:
        izq = "(" + izq + ")"
    derecha_libre = isinstance(f, (And, Or)) and type(f.b) is type(f)
    if _prec(f.b) < 5 and not derecha_libre:
        der = "(" + der + ")"
    return izq + _SIMB[type(f)] + der


# --------------------------------------------------------------------------
# Semántica
# --------------------------------------------------------------------------


def variables(f: Form) -> List[str]:
    """Nombres de las proposiciones elementales, en orden alfabético."""
    vistas = set()

    def rec(g: Form) -> None:
        if isinstance(g, Var):
            vistas.add(g.nombre)
        elif isinstance(g, Not):
            rec(g.a)
        elif isinstance(g, (And, Or, Imp, Iff)):
            rec(g.a)
            rec(g.b)

    rec(f)
    return sorted(vistas)


def valuar(f: Form, v: Dict[str, bool]) -> bool:
    """Valor de verdad de f bajo la valuación v."""
    if isinstance(f, Var):
        return v[f.nombre]
    if isinstance(f, Const):
        return f.valor
    if isinstance(f, Not):
        return not valuar(f.a, v)
    if isinstance(f, And):
        return valuar(f.a, v) and valuar(f.b, v)
    if isinstance(f, Or):
        return valuar(f.a, v) or valuar(f.b, v)
    if isinstance(f, Imp):
        return (not valuar(f.a, v)) or valuar(f.b, v)
    if isinstance(f, Iff):
        return valuar(f.a, v) == valuar(f.b, v)
    raise TypeError(f"Fórmula desconocida: {f!r}")


def valuaciones(nombres: List[str]) -> List[Dict[str, bool]]:
    """Todas las filas posibles de la tabla de verdad (V primero, como en clase)."""
    return [
        dict(zip(nombres, combo))
        for combo in product([True, False], repeat=len(nombres))
    ]


def tabla(f: Form) -> Tuple[List[str], List[Tuple[Dict[str, bool], bool]]]:
    nombres = variables(f)
    return nombres, [(v, valuar(f, v)) for v in valuaciones(nombres)]


def equivalentes(f: Form, g: Form) -> bool:
    nombres = sorted(set(variables(f)) | set(variables(g)))
    return all(valuar(f, v) == valuar(g, v) for v in valuaciones(nombres))


def es_tautologia(f: Form) -> bool:
    return all(val for _, val in tabla(f)[1])


def es_contradiccion(f: Form) -> bool:
    return not any(val for _, val in tabla(f)[1])


def clasificar(f: Form) -> str:
    if es_tautologia(f):
        return "tautología"
    if es_contradiccion(f):
        return "contradicción"
    return "contingencia"


def tamanio(f: Form) -> int:
    """Cantidad de nodos: sirve para comparar 'qué tan simple' es una fórmula."""
    if isinstance(f, (Var, Const)):
        return 1
    if isinstance(f, Not):
        return 1 + tamanio(f.a)
    return 1 + tamanio(f.a) + tamanio(f.b)


def subformulas(f: Form) -> List[Form]:
    """Todas las subfórmulas (incluida f), en pre-orden."""
    out = [f]
    if isinstance(f, Not):
        out += subformulas(f.a)
    elif isinstance(f, (And, Or, Imp, Iff)):
        out += subformulas(f.a) + subformulas(f.b)
    return out


def reemplazar(f: Form, viejo: Form, nuevo: Form, _hecho=None) -> Form:
    """Reemplaza la primera aparición (pre-orden) de `viejo` por `nuevo`."""
    if _hecho is None:
        _hecho = [False]
    if _hecho[0]:
        return f
    if f == viejo:
        _hecho[0] = True
        return nuevo
    if isinstance(f, Not):
        return Not(reemplazar(f.a, viejo, nuevo, _hecho))
    if isinstance(f, (And, Or, Imp, Iff)):
        a = reemplazar(f.a, viejo, nuevo, _hecho)
        b = reemplazar(f.b, viejo, nuevo, _hecho)
        return type(f)(a, b)
    return f


def tabla_markdown(f: Form) -> str:
    """Tabla de verdad completa en formato Markdown."""
    nombres, filas = tabla(f)
    cab = "| " + " | ".join(nombres) + f" | {escribir(f)} |"
    sep = "|" + "|".join(["---"] * (len(nombres) + 1)) + "|"
    cuerpo = []
    for v, val in filas:
        celdas = ["V" if v[n] else "F" for n in nombres]
        celdas.append("**V**" if val else "**F**")
        cuerpo.append("| " + " | ".join(celdas) + " |")
    return "\n".join([cab, sep] + cuerpo)
