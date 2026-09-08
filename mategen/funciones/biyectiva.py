"""Inyectividad, sobreyectividad, redefinición y función inversa.

Cada plantilla conoce su dominio natural, su imagen y su inversa. Antes de
proponer el ejercicio se verifica numéricamente que f⁻¹(f(x)) = x en muchos
puntos del dominio, así que la inversa de la resolución está comprobada.
"""

import math
import random
from fractions import Fraction
from typing import Dict

from .intervalos import Dominio, Intervalo, desde, num, reales, reales_sin
from .notacion import anteponer, coef, desplazar, dividir, parentizar, sumar


def generar(rng: random.Random) -> Dict:
    tipo = rng.choice(["homografica", "cuadratica", "exponencial", "logaritmica", "raiz"])
    h = rng.choice([x for x in range(-4, 5) if x != 0])
    k = rng.choice([x for x in range(-4, 5) if x != 0])

    if tipo == "homografica":
        # f(x) = (a x + b) / (x + c). Se exige a·c ≠ b: si fueran iguales la
        # función sería constante y no inyectiva.
        while True:
            a = rng.choice([1, 2, 3])
            b = rng.choice([x for x in range(-6, 7) if x != 0])
            c = rng.choice([x for x in range(-5, 6) if x != 0])
            if a * c != b:
                break
        num_txt = sumar(coef(a, "x"), b)
        den_txt = sumar("x", c)
        texto = f"f(x) = ({num_txt}) / ({den_txt})"
        dominio = reales_sin([-c])
        natural = dominio                     # ya es biyectiva sobre su imagen
        imagen = reales_sin([a])
        inyectiva, sobreyectiva = True, False
        f = lambda x: (a * x + b) / (x + c)
        finv = lambda y: (b - c * y) / (y - a)
        inv_num = sumar(coef(-c, "x"), b)
        inversa_texto = f"f⁻¹(x) = ({inv_num}) / ({desplazar('x', a)})"
        analisis = (
            f"**Inyectividad.** Supongamos f(x₁) = f(x₂). Multiplicando en cruz y "
            f"desarrollando, los términos en x₁·x₂ se cancelan y queda\n\n"
            f"({num(a * c - b)})·x₁ = ({num(a * c - b)})·x₂\n\n"
            f"Como a·c − b = {num(a)}·{num(c)} − ({num(b)}) = {num(a * c - b)} ≠ 0, se puede "
            f"simplificar y resulta x₁ = x₂. **Es inyectiva.**\n\n"
            f"**Sobreyectividad.** Con codominio ℝ **no** es sobreyectiva: al despejar x "
            f"aparece (y − {num(a)}) en el denominador, así que y = {num(a)} no tiene "
            f"preimagen. Esa es justamente la asíntota horizontal."
        )
        despeje = (
            f"y = ({num_txt}) / ({den_txt})\n\n"
            f"y·({den_txt}) = {num_txt}      (paso el denominador multiplicando)\n\n"
            f"xy {'+' if c > 0 else '−'} {num(abs(c))}y = {coef(a, 'x')} "
            f"{'+' if b > 0 else '−'} {num(abs(b))}\n\n"
            f"xy − {coef(a, 'x')} = {num(b)} − {coef(c, 'y')}      (agrupo lo que tiene x)\n\n"
            f"x·({desplazar('y', a)}) = {sumar(coef(-c, 'y'), b)}\n\n"
            f"x = ({sumar(coef(-c, 'y'), b)}) / ({desplazar('y', a)})"
        )
        redefinir = f"Alcanza con tomar como codominio {imagen}: f : {dominio} → {imagen} ya es biyectiva."
    elif tipo == "cuadratica":
        a = rng.choice([1, 2])
        cuerpo = f"{coef(a, parentizar(desplazar('x', h)) + '²')}"
        texto = f"f(x) = {sumar(cuerpo, k)}"
        # Ojo: el dominio **natural** de una cuadrática es todo ℝ. El intervalo
        # [h ; +∞) aparece recién en c), al restringir para que admita inversa.
        natural = reales()
        dominio = desde(h, True)
        imagen = desde(k, True)
        inyectiva, sobreyectiva = False, False
        f = lambda x: a * (x - h) ** 2 + k
        finv = lambda y: h + math.sqrt((y - k) / a)
        inversa_texto = f"f⁻¹(x) = {anteponer(h, '√(' + dividir(desplazar('x', k), a) + ')')}"
        analisis = (
            f"**Inyectividad.** En ℝ **no** es inyectiva: la parábola es simétrica respecto "
            f"del eje x = {num(h)}, así que dos puntos equidistantes del vértice tienen la "
            f"misma imagen. Por ejemplo f({num(h - 1)}) = f({num(h + 1)}) = {num(a + k)}.\n\n"
            f"**Sobreyectividad.** Con codominio ℝ tampoco: el coeficiente principal "
            f"{num(a)} es positivo, así que el vértice ({num(h)} ; {num(k)}) es un **mínimo** "
            f"y ningún valor menor que {num(k)} se alcanza. Im f = {imagen}."
        )
        despeje = (
            f"y = {sumar(cuerpo, k)}\n\n"
            f"{desplazar('y', k)} = {cuerpo}\n\n"
            f"{dividir(desplazar('y', k), a)} = ({desplazar('x', h)})²\n\n"
            f"√({dividir(desplazar('y', k), a)}) = {desplazar('x', h)}      "
            f"(tomo la raíz positiva porque en la restricción x ≥ {num(h)})\n\n"
            f"x = {anteponer(h, '√(' + dividir(desplazar('y', k), a) + ')')}"
        )
        redefinir = (
            f"Hay que hacer **dos** cosas: restringir el dominio a una sola rama de la "
            f"parábola y ajustar el codominio a la imagen.\n\n"
            f"f : {dominio} → {imagen}  (rama derecha del vértice)"
        )
    elif tipo == "exponencial":
        a = rng.choice([1, 2])
        cuerpo = coef(a, f"e^({desplazar('x', h)})")
        texto = f"f(x) = {sumar(cuerpo, k)}"
        dominio = reales()
        natural = dominio
        imagen = Dominio([Intervalo(k, None, False, False)])
        inyectiva, sobreyectiva = True, False
        f = lambda x: a * math.exp(x - h) + k
        finv = lambda y: h + math.log((y - k) / a)
        inversa_texto = f"f⁻¹(x) = {anteponer(h, 'ln(' + dividir(desplazar('x', k), a) + ')')}"
        analisis = (
            f"**Inyectividad.** La exponencial es estrictamente creciente; multiplicarla por "
            f"{num(a)} > 0 y sumarle una constante no cambia el crecimiento. Una función "
            f"estrictamente creciente es **inyectiva**.\n\n"
            f"**Sobreyectividad.** Con codominio ℝ no lo es: e^({desplazar('x', h)}) > 0 "
            f"para todo x, así que f(x) > {num(k)} siempre. Im f = {imagen}, y la recta "
            f"y = {num(k)} es asíntota horizontal."
        )
        despeje = (
            f"y = {sumar(cuerpo, k)}\n\n"
            f"{desplazar('y', k)} = {cuerpo}\n\n"
            f"{dividir(desplazar('y', k), a)} = e^({desplazar('x', h)})\n\n"
            f"ln({dividir(desplazar('y', k), a)}) = {desplazar('x', h)}      "
            f"(aplico ln, que es la inversa de la exponencial)\n\n"
            f"x = {anteponer(h, 'ln(' + dividir(desplazar('y', k), a) + ')')}"
        )
        redefinir = f"Basta con ajustar el codominio: f : ℝ → {imagen} es biyectiva."
    elif tipo == "logaritmica":
        a = rng.choice([1, 2])
        cuerpo = coef(a, f"ln({desplazar('x', h)})")
        texto = f"f(x) = {sumar(cuerpo, k)}"
        dominio = Dominio([Intervalo(h, None, False, False)])
        natural = dominio
        imagen = reales()
        inyectiva, sobreyectiva = True, True
        f = lambda x: a * math.log(x - h) + k
        finv = lambda y: h + math.exp((y - k) / a)
        inversa_texto = f"f⁻¹(x) = {anteponer(h, 'e^(' + dividir(desplazar('x', k), a) + ')')}"
        analisis = (
            f"**Inyectividad.** ln es estrictamente creciente en su dominio y "
            f"{'multiplicar por ' + num(a) + ' > 0 y ' if a != 1 else ''}sumar {num(k)} "
            f"mantiene el crecimiento: **es inyectiva**.\n\n"
            f"**Sobreyectividad.** Con codominio ℝ **sí** lo es: cuando x recorre "
            f"({num(h)} ; +∞), ln({desplazar('x', h)}) toma todos los valores reales. "
            f"Al ser inyectiva y sobreyectiva, **ya es biyectiva** y no hace falta "
            f"redefinir nada."
        )
        despeje = (
            f"y = {sumar(cuerpo, k)}\n\n"
            f"{desplazar('y', k)} = {cuerpo}\n\n"
            f"{dividir(desplazar('y', k), a)} = ln({desplazar('x', h)})\n\n"
            f"e^({dividir(desplazar('y', k), a)}) = {desplazar('x', h)}      "
            f"(aplico la exponencial a ambos miembros)\n\n"
            f"x = {anteponer(h, 'e^(' + dividir(desplazar('y', k), a) + ')')}"
        )
        redefinir = "No hace falta redefinir: con dominio natural y codominio ℝ ya es biyectiva."
    else:  # raiz
        a = 1
        cuerpo = f"√({desplazar('x', h)})"
        texto = f"f(x) = {sumar(cuerpo, k)}"
        dominio = desde(h, True)
        natural = dominio
        imagen = desde(k, True)
        inyectiva, sobreyectiva = True, False
        f = lambda x: math.sqrt(x - h) + k
        finv = lambda y: (y - k) ** 2 + h
        inversa_texto = f"f⁻¹(x) = {sumar('(' + desplazar('x', k) + ')²', h)}"
        analisis = (
            f"**Inyectividad.** √ es estrictamente creciente en [{num(h)} ; +∞), así que "
            f"**es inyectiva**.\n\n"
            f"**Sobreyectividad.** Con codominio ℝ no lo es: √({desplazar('x', h)}) ≥ 0, "
            f"entonces f(x) ≥ {num(k)}. Im f = {imagen}."
        )
        despeje = (
            f"y = {sumar(cuerpo, k)}\n\n"
            f"{desplazar('y', k)} = √({desplazar('x', h)})\n\n"
            f"({desplazar('y', k)})² = {desplazar('x', h)}      "
            f"(elevo al cuadrado: es válido porque ambos miembros son ≥ 0)\n\n"
            f"x = {sumar('(' + desplazar('y', k) + ')²', h)}"
        )
        redefinir = f"Basta con ajustar el codominio: f : {dominio} → {imagen} es biyectiva."

    return {
        "tipo": tipo,
        "texto": texto,
        # `dominio` es aquel donde f resulta biyectiva (para la cuadrática, ya
        # restringido); `dominio_natural` es el que se pide en el inciso a).
        "dominio": dominio,
        "dominio_natural": natural,
        "inyectiva": inyectiva,
        "sobreyectiva": sobreyectiva,
        "imagen": imagen,
        "inversa_texto": inversa_texto,
        "f": f,
        "finv": finv,
        "analisis": analisis,
        "despeje": despeje,
        "redefinir": redefinir,
    }


def verificar(ej: Dict, muestras: int = 400) -> bool:
    """Comprueba que f⁻¹(f(x)) = x y que f(x) cae en la imagen declarada."""
    f, finv, dom = ej["f"], ej["finv"], ej["dominio"]
    probados = 0
    for i in range(muestras):
        x = -10 + 20 * i / muestras
        if not dom.contiene(x):
            continue
        try:
            y = f(x)
        except (ValueError, ZeroDivisionError):
            return False
        if not ej["imagen"].contiene(y):
            return False
        if abs(finv(y) - x) > 1e-7:
            return False
        probados += 1
    return probados > 10
