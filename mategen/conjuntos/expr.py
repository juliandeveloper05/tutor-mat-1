"""Expresiones de conjuntos: escritura, simplificación y verificación.

El álgebra de conjuntos y la lógica proposicional son la misma álgebra de Boole:
∪ se comporta como ∨, ∩ como ∧ y el complemento como ¬. Por eso este módulo
traduce la expresión a una fórmula, reutiliza el simplificador de `logica.leyes`
y vuelve a traducir, renombrando cada ley a su nombre conjuntista.
"""

import random
from dataclasses import dataclass
from itertools import product
from typing import Dict, List, Optional, Tuple

from ..logica import formula as L
from ..logica.leyes import simplificar


class SExpr:
    def __str__(self) -> str:  # pragma: no cover
        return escribir(self)


@dataclass(frozen=True)
class SVar(SExpr):
    nombre: str


@dataclass(frozen=True)
class Universo(SExpr):
    pass


@dataclass(frozen=True)
class Vacio(SExpr):
    pass


@dataclass(frozen=True)
class Comp(SExpr):
    a: SExpr


@dataclass(frozen=True)
class Union(SExpr):
    a: SExpr
    b: SExpr


@dataclass(frozen=True)
class Inter(SExpr):
    a: SExpr
    b: SExpr


@dataclass(frozen=True)
class Dif(SExpr):
    a: SExpr
    b: SExpr


_OVERLINE = "̅"


def escribir(e: SExpr) -> str:
    if isinstance(e, SVar):
        return e.nombre
    if isinstance(e, Universo):
        return "U"
    if isinstance(e, Vacio):
        return "∅"
    if isinstance(e, Comp):
        interno = escribir(e.a)
        if isinstance(e.a, (SVar, Universo, Vacio)):
            return interno + _OVERLINE          # A̅
        return "(" + interno + ")ᶜ"             # (A ∪ B)ᶜ
    izq, der = escribir(e.a), escribir(e.b)
    if isinstance(e.a, (Union, Inter, Dif)) and type(e.a) is not type(e):
        izq = "(" + izq + ")"
    if isinstance(e.b, (Union, Inter, Dif)):
        der = "(" + der + ")"
    simbolo = {Union: " ∪ ", Inter: " ∩ ", Dif: " − "}[type(e)]
    return izq + simbolo + der


def escribir_latex(e: SExpr) -> str:
    """La misma expresión en LaTeX, para renderizar con KaTeX en el frontend.

    En LaTeX el complemento se escribe siempre con barra arriba —
    \\overline{A}, \\overline{A \\cup B}— que es como se escribe a mano, así que
    no hace falta la variante con exponente c.
    """
    if isinstance(e, SVar):
        return e.nombre
    if isinstance(e, Universo):
        return "U"
    if isinstance(e, Vacio):
        return r"\emptyset"
    if isinstance(e, Comp):
        return r"\overline{" + escribir_latex(e.a) + "}"
    izq, der = escribir_latex(e.a), escribir_latex(e.b)
    if isinstance(e.a, (Union, Inter, Dif)) and type(e.a) is not type(e):
        izq = "(" + izq + ")"
    if isinstance(e.b, (Union, Inter, Dif)):
        der = "(" + der + ")"
    simbolo = {Union: r" \cup ", Inter: r" \cap ", Dif: " - "}[type(e)]
    return izq + simbolo + der


# --------------------------------------------------------------------------
# Traducción a fórmulas proposicionales (x ∈ A  ↔  la variable A es verdadera)
# --------------------------------------------------------------------------


def a_formula(e: SExpr) -> L.Form:
    if isinstance(e, SVar):
        return L.Var(e.nombre)
    if isinstance(e, Universo):
        return L.Const(True)
    if isinstance(e, Vacio):
        return L.Const(False)
    if isinstance(e, Comp):
        return L.Not(a_formula(e.a))
    if isinstance(e, Union):
        return L.Or(a_formula(e.a), a_formula(e.b))
    if isinstance(e, Inter):
        return L.And(a_formula(e.a), a_formula(e.b))
    if isinstance(e, Dif):
        return L.And(a_formula(e.a), L.Not(a_formula(e.b)))
    raise TypeError(e)


def a_conjunto(f: L.Form) -> SExpr:
    if isinstance(f, L.Var):
        return SVar(f.nombre)
    if isinstance(f, L.Const):
        return Universo() if f.valor else Vacio()
    if isinstance(f, L.Not):
        return Comp(a_conjunto(f.a))
    if isinstance(f, L.Or):
        return Union(a_conjunto(f.a), a_conjunto(f.b))
    if isinstance(f, L.And):
        return Inter(a_conjunto(f.a), a_conjunto(f.b))
    raise TypeError(f"La fórmula {L.escribir(f)} no tiene traducción conjuntista")


NOMBRE_LEY = {
    "Negación de una constante": "Complemento de U y de ∅",
    "Doble negación": "Doble complemento",
    "Ley del complemento": "Ley del complemento",
    "Ley de dominación": "Ley de dominación",
    "Ley de identidad": "Ley de identidad",
    "Idempotencia": "Idempotencia",
    "Ley de absorción": "Ley de absorción",
    "Ley de absorción (2ª forma)": "Ley de absorción (2ª forma)",
    "Ley distributiva (factor común)": "Ley distributiva (factor común)",
    "Ley de De Morgan": "Ley de De Morgan",
}


def tiene_diferencia(e: SExpr) -> bool:
    if isinstance(e, Dif):
        return True
    if isinstance(e, Comp):
        return tiene_diferencia(e.a)
    if isinstance(e, (Union, Inter)):
        return tiene_diferencia(e.a) or tiene_diferencia(e.b)
    return False


def quitar_diferencias(e: SExpr) -> SExpr:
    """Reescribe A − B como A ∩ B̅ (definición de diferencia)."""
    if isinstance(e, Dif):
        return Inter(quitar_diferencias(e.a), Comp(quitar_diferencias(e.b)))
    if isinstance(e, Comp):
        return Comp(quitar_diferencias(e.a))
    if isinstance(e, Union):
        return Union(quitar_diferencias(e.a), quitar_diferencias(e.b))
    if isinstance(e, Inter):
        return Inter(quitar_diferencias(e.a), quitar_diferencias(e.b))
    return e


def simplificar_conjunto(e: SExpr) -> Tuple[SExpr, List[Tuple[str, SExpr]]]:
    """Simplifica paso a paso. Devuelve (resultado, [(ley, expresión), ...])."""
    pasos: List[Tuple[str, SExpr]] = []
    actual = e
    if tiene_diferencia(e):
        actual = quitar_diferencias(e)
        pasos.append(("Definición de diferencia (A − B = A ∩ B̅)", actual))
    final_formula, pasos_logicos = simplificar(a_formula(actual))
    for nombre, _antes, _despues, completa in pasos_logicos:
        pasos.append((NOMBRE_LEY.get(nombre, nombre), a_conjunto(completa)))
    return a_conjunto(final_formula), pasos


def variables(e: SExpr) -> List[str]:
    return L.variables(a_formula(e))


def evaluar_celdas(e: SExpr, nombres: List[str]) -> frozenset:
    """Interpreta la expresión en el álgebra de Boole libre.

    Cada "celda" es una de las 2^n regiones del diagrama de Venn: la expresión
    queda representada por el conjunto exacto de regiones que ocupa, así que dos
    expresiones son iguales si y sólo si tienen las mismas celdas.
    """
    f = a_formula(e)
    celdas = set()
    for combo in product([True, False], repeat=len(nombres)):
        v = dict(zip(nombres, combo))
        if L.valuar(f, v):
            celdas.add(combo)
    return frozenset(celdas)


def iguales(e1: SExpr, e2: SExpr) -> bool:
    nombres = sorted(set(variables(e1)) | set(variables(e2)))
    return evaluar_celdas(e1, nombres) == evaluar_celdas(e2, nombres)


# --------------------------------------------------------------------------
# Generación: se complica una expresión simple aplicando leyes al revés
# --------------------------------------------------------------------------


def _subexpresiones(e: SExpr) -> List[SExpr]:
    salida = [e]
    if isinstance(e, Comp):
        salida += _subexpresiones(e.a)
    elif isinstance(e, (Union, Inter, Dif)):
        salida += _subexpresiones(e.a) + _subexpresiones(e.b)
    return salida


def _reemplazar(e: SExpr, viejo: SExpr, nuevo: SExpr, hecho=None) -> SExpr:
    if hecho is None:
        hecho = [False]
    if hecho[0]:
        return e
    if e == viejo:
        hecho[0] = True
        return nuevo
    if isinstance(e, Comp):
        return Comp(_reemplazar(e.a, viejo, nuevo, hecho))
    if isinstance(e, (Union, Inter, Dif)):
        return type(e)(
            _reemplazar(e.a, viejo, nuevo, hecho), _reemplazar(e.b, viejo, nuevo, hecho)
        )
    return e


def complicar(objetivo: SExpr, pasos: int, rng: random.Random, extras: List[SExpr]) -> SExpr:
    actual = objetivo
    for _ in range(pasos):
        sub = rng.choice(_subexpresiones(actual))
        usadas = set(variables(sub))
        libres = [x for x in extras if x.nombre not in usadas] or extras
        v = rng.choice(libres)
        opciones: List[SExpr] = [
            Comp(Comp(sub)),
            Inter(sub, Universo()),
            Union(sub, Vacio()),
            Union(sub, Inter(sub, v)),
            Inter(sub, Union(sub, v)),
            Union(sub, Inter(v, Comp(v))),
            Inter(sub, Union(v, Comp(v))),
            Dif(sub, Comp(sub)) if isinstance(sub, SVar) else Inter(sub, Universo()),
        ]
        if isinstance(sub, Union):
            opciones.append(Comp(Inter(Comp(sub.a), Comp(sub.b))))
        if isinstance(sub, Inter):
            opciones.append(Comp(Union(Comp(sub.a), Comp(sub.b))))
            if isinstance(sub.b, Union):
                opciones.append(Union(Inter(sub.a, sub.b.a), Inter(sub.a, sub.b.b)))
        if isinstance(sub, Inter) and isinstance(sub.b, Comp):
            opciones.append(Dif(sub.a, sub.b.a))
        actual = _reemplazar(actual, sub, rng.choice(opciones))
    return actual


def generar_identidad(rng: random.Random, dificultad: int = 3):
    """Devuelve (expresión, resultado, pasos) para 'demostrar que ... = ...'."""
    A, B, C = SVar("A"), SVar("B"), SVar("C")
    objetivos = [B, A, Union(A, B), Inter(A, B), Union(A, Inter(B, C)), Dif(A, B)]
    for _ in range(600):
        objetivo = rng.choice(objetivos)
        enunciado = complicar(objetivo, dificultad, rng, [A, B, C])
        texto = escribir(enunciado)
        if not (14 <= len(texto) <= 60):
            continue
        if len({c for c in texto if c in "ABC"}) < 2:
            continue
        resultado, pasos = simplificar_conjunto(enunciado)
        if not (3 <= len(pasos) <= 10):
            continue
        if not iguales(enunciado, objetivo) or not iguales(resultado, objetivo):
            continue
        return enunciado, resultado, pasos
    raise RuntimeError("No se pudo generar la identidad de conjuntos")
