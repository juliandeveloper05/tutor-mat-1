"""Leyes lógicas: simplificación paso a paso y generación de enunciados.

La simplificación aplica leyes con nombre (las del apunte) y registra cada paso,
igual que se pide en el parcial: una cadena de equivalencias justificada.

La generación funciona al revés: parte de una fórmula simple (la respuesta) y le
aplica leyes "hacia atrás" para complicarla. Así el ejercicio propuesto siempre
tiene una solución conocida y alcanzable.
"""

import random
from typing import Callable, List, Optional, Tuple

from .formula import (
    And,
    Const,
    Form,
    Iff,
    Imp,
    Not,
    Or,
    Var,
    equivalentes,
    escribir,
    reemplazar,
    subformulas,
    tamanio,
)

V = Const(True)
F = Const(False)


# --------------------------------------------------------------------------
# Leyes de simplificación: cada una recibe un nodo y devuelve el nodo reescrito
# (o None si no se aplica).
# --------------------------------------------------------------------------


def _ley_bicondicional(n: Form) -> Optional[Form]:
    if isinstance(n, Iff):
        return And(Imp(n.a, n.b), Imp(n.b, n.a))
    return None


def _ley_condicional(n: Form) -> Optional[Form]:
    if isinstance(n, Imp):
        return Or(Not(n.a), n.b)
    return None


def _negacion_de_constante(n: Form) -> Optional[Form]:
    if isinstance(n, Not) and isinstance(n.a, Const):
        return Const(not n.a.valor)
    return None


def _doble_negacion(n: Form) -> Optional[Form]:
    if isinstance(n, Not) and isinstance(n.a, Not):
        return n.a.a
    return None


def _de_morgan(n: Form) -> Optional[Form]:
    if isinstance(n, Not):
        if isinstance(n.a, And):
            return Or(Not(n.a.a), Not(n.a.b))
        if isinstance(n.a, Or):
            return And(Not(n.a.a), Not(n.a.b))
    return None


def _idempotencia(n: Form) -> Optional[Form]:
    if isinstance(n, (And, Or)) and n.a == n.b:
        return n.a
    return None


def _complemento(n: Form) -> Optional[Form]:
    """p ∧ ¬p ≡ F   y   p ∨ ¬p ≡ V."""
    if isinstance(n, (And, Or)):
        if n.b == Not(n.a) or n.a == Not(n.b):
            return Const(isinstance(n, Or))
    return None


def _identidad(n: Form) -> Optional[Form]:
    """p ∧ V ≡ p   y   p ∨ F ≡ p."""
    if isinstance(n, And):
        if n.a == V:
            return n.b
        if n.b == V:
            return n.a
    if isinstance(n, Or):
        if n.a == F:
            return n.b
        if n.b == F:
            return n.a
    return None


def _dominacion(n: Form) -> Optional[Form]:
    """p ∨ V ≡ V   y   p ∧ F ≡ F."""
    if isinstance(n, Or) and (n.a == V or n.b == V):
        return V
    if isinstance(n, And) and (n.a == F or n.b == F):
        return F
    return None


def _absorcion(n: Form) -> Optional[Form]:
    """p ∨ (p ∧ q) ≡ p   y   p ∧ (p ∨ q) ≡ p (en cualquier orden)."""
    if isinstance(n, Or):
        for x, y in ((n.a, n.b), (n.b, n.a)):
            if isinstance(y, And) and (y.a == x or y.b == x):
                return x
    if isinstance(n, And):
        for x, y in ((n.a, n.b), (n.b, n.a)):
            if isinstance(y, Or) and (y.a == x or y.b == x):
                return x
    return None


def _absorcion_2(n: Form) -> Optional[Form]:
    """p ∨ (¬p ∧ q) ≡ p ∨ q   y   p ∧ (¬p ∨ q) ≡ p ∧ q."""
    if isinstance(n, Or):
        for x, y in ((n.a, n.b), (n.b, n.a)):
            if isinstance(y, And):
                if y.a == Not(x) or Not(y.a) == x:
                    return Or(x, y.b)
                if y.b == Not(x) or Not(y.b) == x:
                    return Or(x, y.a)
    if isinstance(n, And):
        for x, y in ((n.a, n.b), (n.b, n.a)):
            if isinstance(y, Or):
                if y.a == Not(x) or Not(y.a) == x:
                    return And(x, y.b)
                if y.b == Not(x) or Not(y.b) == x:
                    return And(x, y.a)
    return None


def _distributiva_factor(n: Form) -> Optional[Form]:
    """(p ∧ q) ∨ (p ∧ r) ≡ p ∧ (q ∨ r)  y su dual: se saca factor común."""
    if isinstance(n, Or) and isinstance(n.a, And) and isinstance(n.b, And):
        interno, externo = And, Or
    elif isinstance(n, And) and isinstance(n.a, Or) and isinstance(n.b, Or):
        interno, externo = Or, And
    else:
        return None
    izq, der = n.a, n.b
    for x in (izq.a, izq.b):
        for y in (der.a, der.b):
            if x == y:
                resto_izq = izq.b if x == izq.a else izq.a
                resto_der = der.b if y == der.a else der.a
                return interno(x, externo(resto_izq, resto_der))
    return None


# Orden de aplicación. Primero las leyes que *achican* la fórmula (para no dar
# vueltas de más) y sólo cuando ninguna se aplica se recurre a las que cambian
# la estructura (De Morgan, condicional, bicondicional). Con este orden las
# derivaciones quedan cortas y se parecen a las que se escriben en el parcial.
LEYES: List[Tuple[str, Callable[[Form], Optional[Form]]]] = [
    ("Negación de una constante", _negacion_de_constante),
    ("Doble negación", _doble_negacion),
    ("Ley del complemento", _complemento),
    ("Ley de dominación", _dominacion),
    ("Ley de identidad", _identidad),
    ("Idempotencia", _idempotencia),
    ("Ley de absorción", _absorcion),
    ("Ley de absorción (2ª forma)", _absorcion_2),
    ("Ley distributiva (factor común)", _distributiva_factor),
    ("Ley de De Morgan", _de_morgan),
    ("Ley del bicondicional", _ley_bicondicional),
    ("Ley del condicional", _ley_condicional),
]


def un_paso(f: Form) -> Optional[Tuple[str, Form, Form, Form]]:
    """Busca la primera ley aplicable.

    Devuelve (nombre_ley, subfórmula_antes, subfórmula_después, fórmula_completa).
    """
    for nombre, ley in LEYES:
        for sub in subformulas(f):
            nuevo = ley(sub)
            if nuevo is not None and nuevo != sub:
                return nombre, sub, nuevo, reemplazar(f, sub, nuevo)
    return None


def simplificar(f: Form, max_pasos: int = 60):
    """Simplifica f registrando cada ley aplicada.

    Devuelve (fórmula_final, pasos) donde cada paso es
    (nombre_ley, subfórmula_antes, subfórmula_después, fórmula_resultante).
    """
    actual = f
    vistas = {actual}
    pasos = []
    for _ in range(max_pasos):
        res = un_paso(actual)
        if res is None:
            break
        nombre, antes, despues, completa = res
        if completa in vistas:  # evita ciclos
            break
        vistas.add(completa)
        pasos.append((nombre, antes, despues, completa))
        actual = completa
    return actual, pasos


# --------------------------------------------------------------------------
# Generación: leyes aplicadas "hacia atrás" para complicar una fórmula simple.
# --------------------------------------------------------------------------


def _inversas(n: Form, extras: List[Form], rng: random.Random) -> List[Form]:
    """Formas equivalentes pero más complejas del nodo n."""
    from .formula import variables

    usadas = set(variables(n))
    libres = [x for x in extras if x.nombre not in usadas] or extras
    v = rng.choice(libres)
    ops: List[Form] = [
        Not(Not(n)),                    # doble negación
        And(n, V),                      # identidad
        Or(n, F),                       # identidad
        And(n, Or(n, v)),               # absorción
        Or(n, And(n, v)),               # absorción
        Or(n, And(v, Not(v))),          # complemento + identidad
        And(n, Or(v, Not(v))),          # complemento + identidad
    ]
    if isinstance(n, Or):
        ops.append(Not(And(Not(n.a), Not(n.b))))   # De Morgan
        if isinstance(n.a, Not):
            ops.append(Imp(n.a.a, n.b))            # ley del condicional
        else:
            ops.append(Imp(Not(n.a), n.b))
    if isinstance(n, And):
        ops.append(Not(Or(Not(n.a), Not(n.b))))    # De Morgan
        if isinstance(n.b, Or):
            ops.append(Or(And(n.a, n.b.a), And(n.a, n.b.b)))  # distributiva
    if isinstance(n, Or) and isinstance(n.b, And):
        ops.append(And(Or(n.a, n.b.a), Or(n.a, n.b.b)))       # distributiva
    return ops


def complicar(objetivo: Form, pasos: int, rng: random.Random, extras: List[Form]) -> Form:
    """Aplica `pasos` transformaciones inversas al azar sobre `objetivo`."""
    actual = objetivo
    for _ in range(pasos):
        candidatas = subformulas(actual)
        sub = rng.choice(candidatas)
        opciones = _inversas(sub, extras, rng)
        nuevo = rng.choice(opciones)
        actual = reemplazar(actual, sub, nuevo)
    return actual


def generar_simplificacion(rng: random.Random, dificultad: int = 4):
    """Devuelve (enunciado, resultado, pasos) de un ejercicio de simplificación.

    Se exige que el ejercicio sea "de parcial": ni trivial ni interminable, con
    al menos dos proposiciones elementales y algún conectivo interesante
    (condicional o una negación sobre una fórmula compuesta). La equivalencia
    entre enunciado y resultado se verifica siempre por tabla de verdad.
    """
    p, q, r = Var("p"), Var("q"), Var("r")
    objetivos = [
        Or(p, q),
        And(p, q),
        Or(Not(p), q),
        And(p, Not(q)),
        Not(p),
        p,
        Imp(p, q),
    ]
    for _ in range(600):
        objetivo = rng.choice(objetivos)
        enunciado = complicar(objetivo, dificultad, rng, [p, q, r])
        if not (8 <= tamanio(enunciado) <= 20):
            continue
        if len(set(v for v in escribir(enunciado) if v in "pqr")) < 2:
            continue
        # que se parezca a un enunciado de parcial
        interesante = any(
            isinstance(s, Imp)
            or (isinstance(s, Not) and isinstance(s.a, (And, Or, Imp, Iff)))
            for s in subformulas(enunciado)
        )
        if not interesante:
            continue
        final, pasos = simplificar(enunciado)
        if not (3 <= len(pasos) <= 12):
            continue
        if not equivalentes(enunciado, final):  # jamás debería fallar
            continue
        if tamanio(final) > tamanio(objetivo):
            continue
        return enunciado, final, pasos
    raise RuntimeError("No se pudo generar el ejercicio de simplificación")
