"""Dominio natural de una función real.

Cada plantilla trae su propia resolución: qué condición hay que pedir (radicando
≥ 0, denominador ≠ 0, argumento del logaritmo > 0), cómo se resuelve esa
inecuación y cuál es el conjunto resultante. El dominio calculado se controla
después evaluando la función en una grilla de puntos.
"""

import math
import random
from fractions import Fraction
from typing import Callable, Dict, List

from .intervalos import Dominio, Intervalo, desde, num, reales, reales_sin
from .notacion import coef, desplazar, sumar


def _cuadratica(s: int, p: int) -> str:
    """Escribe x² − s·x + p sin términos con coeficiente cero."""
    medio = "" if s == 0 else (f" − {num(s)}x" if s > 0 else f" + {num(-s)}x")
    return sumar(f"x²{medio}", p)


def generar(rng: random.Random) -> Dict:
    tipo = rng.choice(["racional", "raiz_lineal", "raiz_sobre_lineal", "log_lineal",
                       "raiz_cuadratica", "log_cuadratica"])
    a = rng.choice([1, 2, 3])
    b = rng.randint(-8, 8)
    c = rng.choice([x for x in range(-5, 6) if x != 0])
    k = rng.choice([2, 3, 4, 5])

    if tipo == "racional":
        texto = f"f(x) = ({sumar('x', b)}) / ({desplazar('x', c)})"
        dominio = reales_sin([c])
        f = lambda x: (x + b) / (x - c)
        pasos = [
            ("Detectar la restricción",
             "Es un cociente de polinomios. Lo único que hay que pedir es que el "
             "**denominador no se anule**, porque la división por cero no está definida."),
            ("Resolver la condición",
             f"{desplazar('x', c)} ≠ 0  ⟺  x ≠ {num(c)}"),
            ("Escribir el dominio",
             f"Dom f = ℝ − {{{num(c)}}} = {dominio}"),
        ]
    elif tipo == "raiz_lineal":
        raiz = Fraction(-b, a)
        texto = f"f(x) = √({sumar(coef(a, 'x'), b)})"
        dominio = desde(raiz, True)
        f = lambda x: math.sqrt(a * x + b)
        pasos = [
            ("Detectar la restricción",
             "En una raíz **de índice par** el radicando no puede ser negativo: hay que "
             "pedir que sea mayor o igual que cero."),
            ("Resolver la inecuación",
             f"{sumar(coef(a, 'x'), b)} ≥ 0  ⟺  {coef(a, 'x')} ≥ {num(-b)}  ⟺  x ≥ {num(raiz)}\n\n"
             f"(el coeficiente {num(a)} es positivo, así que al dividir **no** se da vuelta "
             f"la desigualdad)"),
            ("Escribir el dominio", f"Dom f = {dominio}"),
        ]
    elif tipo == "raiz_sobre_lineal":
        raiz = Fraction(-b, a)
        c = int(math.ceil(float(raiz))) + rng.randint(1, 3)  # el punto excluido cae adentro
        texto = f"f(x) = √({sumar(coef(a, 'x'), b)}) / ({desplazar('x', c)})"
        dominio = Dominio([Intervalo(raiz, None, True, False)], [c])
        f = lambda x: math.sqrt(a * x + b) / (x - c)
        pasos = [
            ("Detectar las restricciones",
             "Hay **dos** condiciones simultáneas: el radicando de la raíz no puede ser "
             "negativo y el denominador no puede anularse. El dominio es la intersección "
             "de ambas."),
            ("Resolver cada una",
             f"1) {sumar(coef(a, 'x'), b)} ≥ 0 ⟺ x ≥ {num(raiz)}\n"
             f"2) {desplazar('x', c)} ≠ 0 ⟺ x ≠ {num(c)}"),
            ("Intersecar",
             f"Como {num(c)} ≥ {num(raiz)}, el punto excluido cae dentro del intervalo y hay "
             f"que sacarlo:\n\nDom f = {dominio}"),
        ]
    elif tipo == "log_lineal":
        h = rng.choice([x for x in range(-5, 6) if x != 0])
        texto = f"f(x) = ln({desplazar('x', h)})"
        dominio = Dominio([Intervalo(h, None, False, False)])
        f = lambda x: math.log(x - h)
        pasos = [
            ("Detectar la restricción",
             "El logaritmo sólo está definido para argumentos **estrictamente positivos**."),
            ("Resolver la inecuación", f"{desplazar('x', h)} > 0  ⟺  x > {num(h)}"),
            ("Escribir el dominio",
             f"Dom f = {dominio}\n\nOjo con el extremo: es **abierto**, porque en x = {num(h)} "
             f"el argumento vale 0 y ln(0) no existe."),
        ]
    elif tipo == "raiz_cuadratica":
        texto = f"f(x) = √(x² − {k * k})"
        dominio = Dominio([Intervalo(None, -k, False, True), Intervalo(k, None, True, False)])
        f = lambda x: math.sqrt(x * x - k * k)
        pasos = [
            ("Detectar la restricción", "Raíz de índice par: el radicando debe ser ≥ 0."),
            ("Resolver la inecuación cuadrática",
             f"x² − {k * k} ≥ 0 ⟺ x² ≥ {k * k} ⟺ |x| ≥ {k} ⟺ x ≤ −{k} **o** x ≥ {k}\n\n"
             f"El error típico acá es escribir sólo x ≥ {k}: hay que acordarse de que "
             f"x² ≥ {k * k} también lo cumplen los negativos de módulo grande."),
            ("Escribir el dominio", f"Dom f = {dominio}"),
        ]
    else:  # log_cuadratica
        r1, r2 = sorted(rng.sample([-3, -2, -1, 1, 2, 3, 4], 2))
        s, p = r1 + r2, r1 * r2
        texto = f"f(x) = ln({_cuadratica(s, p)})"
        dominio = Dominio([Intervalo(None, r1, False, False), Intervalo(r2, None, False, False)])
        f = lambda x: math.log(x * x - s * x + p)
        pasos = [
            ("Detectar la restricción", "El argumento del logaritmo debe ser > 0."),
            ("Factorizar",
             f"{_cuadratica(s, p)} > 0. Las raíces del polinomio son "
             f"x₁ = {num(r1)} y x₂ = {num(r2)}, así que se factoriza como "
             f"({desplazar('x', r1)})({desplazar('x', r2)}) > 0."),
            ("Analizar los signos",
             f"Un producto de dos factores es positivo cuando **ambos tienen el mismo "
             f"signo**:\n\n"
             f"- Los dos negativos: x < {num(r1)}\n"
             f"- Los dos positivos: x > {num(r2)}\n\n"
             f"Entre {num(r1)} y {num(r2)} el producto es negativo, así que ese tramo queda "
             f"afuera."),
            ("Escribir el dominio", f"Dom f = {dominio}"),
        ]

    return {"texto": texto, "dominio": dominio, "pasos": pasos, "f": f, "tipo": tipo}


def verificar(ej: Dict, muestras: int = 900) -> bool:
    """Controla el dominio evaluando la función en una grilla fina.

    Si x está en el dominio calculado, f(x) tiene que poder evaluarse; si no
    está, la evaluación tiene que fallar (dominio de matemática real).
    """
    f, dom = ej["f"], ej["dominio"]
    for i in range(muestras):
        x = -12 + 24 * i / muestras
        dentro = dom.contiene(x)
        try:
            valor = f(x)
            evaluable = isinstance(valor, float) and math.isfinite(valor)
        except (ValueError, ZeroDivisionError):
            evaluable = False
        if dentro != evaluable:
            # Los bordes exactos pueden fallar por redondeo: se toleran.
            if any(abs(x - float(e)) < 1e-6 for e in _bordes(dom)):
                continue
            return False
    return True


def _bordes(dom: Dominio) -> List[float]:
    bordes = [float(e) for e in dom.excluidos]
    for i in dom.intervalos:
        if i.izq is not None:
            bordes.append(float(i.izq))
        if i.der is not None:
            bordes.append(float(i.der))
    return bordes
