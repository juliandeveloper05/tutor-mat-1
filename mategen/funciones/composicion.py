"""Composición de funciones: fórmula y —sobre todo— dominio.

El punto fino de este tema es que el dominio de g∘f **no** se lee de la fórmula
final simplificada: hay que pedir que x esté en el dominio de f y, además, que
f(x) caiga en el dominio de g. El caso (f∘g)(x) = x − c² es el ejemplo clásico:
la fórmula parece definida en todo ℝ, pero el dominio real es [0 ; +∞).
"""

import math
import random
from fractions import Fraction
from typing import Dict

from .intervalos import Dominio, Intervalo, desde, num, reales, reales_sin
from .notacion import coef, desplazar, parentizar, sumar


def generar(rng: random.Random) -> Dict:
    tipo = rng.choice(["lineal_raiz", "cuadratica_raiz", "lineal_inversa", "lineal_log"])
    a = rng.choice([1, 2, 3])
    b = rng.choice([x for x in range(-6, 7) if x != 0])

    if tipo == "lineal_raiz":
        f_txt = f"f(x) = {sumar(coef(a, 'x'), b)}"
        g_txt = "g(x) = √x"
        f = lambda x: a * x + b
        g = lambda x: math.sqrt(x)
        raiz = Fraction(-b, a)
        gf_txt = f"(g ∘ f)(x) = √({sumar(coef(a, 'x'), b)})"
        gf_dom = desde(raiz, True)
        fg_txt = f"(f ∘ g)(x) = {sumar(coef(a, '√x'), b)}"
        fg_dom = desde(0, True)
        razon_gf = (
            f"Dom f = ℝ (es un polinomio), así que la única condición es que f(x) esté en "
            f"Dom g = [0 ; +∞):\n\n"
            f"{sumar(coef(a, 'x'), b)} ≥ 0  ⟺  x ≥ {num(raiz)}"
        )
        razon_fg = (
            "Ahora el orden es al revés: primero actúa g, entonces x debe estar en "
            "Dom g = [0 ; +∞). Después f se puede aplicar a cualquier número real, "
            "así que no agrega restricciones."
        )
    elif tipo == "cuadratica_raiz":
        c = rng.choice([2, 3, 4, 5])
        f_txt = f"f(x) = x² − {c * c}"
        g_txt = "g(x) = √x"
        f = lambda x: x * x - c * c
        g = lambda x: math.sqrt(x)
        gf_txt = f"(g ∘ f)(x) = √(x² − {c * c})"
        gf_dom = Dominio([Intervalo(None, -c, False, True), Intervalo(c, None, True, False)])
        fg_txt = f"(f ∘ g)(x) = x − {c * c}"
        fg_dom = desde(0, True)
        razon_gf = (
            f"Dom f = ℝ, y hay que pedir f(x) ≥ 0:\n\n"
            f"x² − {c * c} ≥ 0 ⟺ x² ≥ {c * c} ⟺ |x| ≥ {c} ⟺ x ≤ −{c} o x ≥ {c}"
        )
        razon_fg = (
            f"**Acá está la trampa clásica.** La fórmula queda (f ∘ g)(x) = (√x)² − {c * c} "
            f"= x − {c * c}, que *parece* definida en todo ℝ. Pero para calcularla hay que "
            f"aplicar primero g, y √x sólo existe si x ≥ 0. El dominio de una composición "
            f"se determina **antes** de simplificar la fórmula, no después."
        )
    elif tipo == "lineal_inversa":
        f_txt = f"f(x) = {sumar(coef(a, 'x'), b)}"
        g_txt = "g(x) = 1 / x"
        f = lambda x: a * x + b
        g = lambda x: 1 / x
        cero = Fraction(-b, a)
        gf_txt = f"(g ∘ f)(x) = 1 / ({sumar(coef(a, 'x'), b)})"
        gf_dom = reales_sin([cero])
        fg_txt = f"(f ∘ g)(x) = {sumar(('1/x' if a == 1 else num(a) + '/x'), b)}"
        fg_dom = reales_sin([0])
        razon_gf = (
            f"Dom f = ℝ y Dom g = ℝ − {{0}}, así que hay que pedir f(x) ≠ 0:\n\n"
            f"{sumar(coef(a, 'x'), b)} ≠ 0  ⟺  x ≠ {num(cero)}"
        )
        razon_fg = (
            "Primero actúa g, que necesita x ≠ 0. Después f acepta cualquier real, "
            "así que no agrega condiciones."
        )
    else:  # lineal_log
        h = rng.choice([x for x in range(-4, 5) if x != 0])
        f_txt = f"f(x) = {desplazar('x', h)}"
        g_txt = "g(x) = ln x"
        f = lambda x: x - h
        g = lambda x: math.log(x)
        gf_txt = f"(g ∘ f)(x) = ln({desplazar('x', h)})"
        gf_dom = Dominio([Intervalo(h, None, False, False)])
        fg_txt = f"(f ∘ g)(x) = {desplazar('ln x', h)}"
        fg_dom = Dominio([Intervalo(0, None, False, False)])
        razon_gf = (
            f"Dom f = ℝ y Dom g = (0 ; +∞), así que hay que pedir f(x) > 0:\n\n"
            f"{desplazar('x', h)} > 0  ⟺  x > {num(h)}"
        )
        razon_fg = (
            "Invirtiendo el orden, primero se aplica ln, que exige x > 0; restar una "
            "constante después no restringe nada."
        )

    return {
        "tipo": tipo,
        "f_texto": f_txt,
        "g_texto": g_txt,
        "f": f,
        "g": g,
        "gf_texto": gf_txt,
        "gf_dominio": gf_dom,
        "gf_razon": razon_gf,
        "fg_texto": fg_txt,
        "fg_dominio": fg_dom,
        "fg_razon": razon_fg,
    }


def _definida(func, x):
    try:
        v = func(x)
        return isinstance(v, float) and math.isfinite(v) or isinstance(v, int)
    except (ValueError, ZeroDivisionError, OverflowError):
        return False


def verificar(ej: Dict, muestras: int = 900) -> bool:
    """Comprueba los dos dominios evaluando las composiciones punto a punto."""
    f, g = ej["f"], ej["g"]
    for i in range(muestras):
        x = -12 + 24 * i / muestras
        # g ∘ f
        posible = _definida(f, x) and _definida(g, f(x))
        if posible != ej["gf_dominio"].contiene(x) and not _borde(ej["gf_dominio"], x):
            return False
        # f ∘ g
        posible2 = _definida(g, x) and _definida(f, g(x))
        if posible2 != ej["fg_dominio"].contiene(x) and not _borde(ej["fg_dominio"], x):
            return False
    return True


def _borde(dom: Dominio, x: float, tol: float = 1e-6) -> bool:
    bordes = [float(e) for e in dom.excluidos]
    for i in dom.intervalos:
        if i.izq is not None:
            bordes.append(float(i.izq))
        if i.der is not None:
            bordes.append(float(i.der))
    return any(abs(x - b) < tol for b in bordes)
