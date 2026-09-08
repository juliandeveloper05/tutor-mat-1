"""Serialización a JSON de todo lo que el frontend necesita dibujar.

Regla del módulo: la verdad matemática vive en Python. Acá no se calcula nada
nuevo — sólo se traduce a JSON lo que los generadores ya produjeron y los tests
ya verificaron. Si el frontend necesita graficar una función, se le mandan los
puntos muestreados desde acá, para que no exista una segunda implementación de
la matemática que se pueda desincronizar de la primera.
"""

from fractions import Fraction
from typing import Callable, Dict, List, Optional, Sequence

from .conjuntos import expr as cexpr
from .ejercicio import Ejercicio
from .funciones.intervalos import Dominio, Intervalo
from .logica import formula as L
from .relaciones.orden import Orden, niveles


# --------------------------------------------------------------------------
# Números
# --------------------------------------------------------------------------

def fraccion_a_json(x) -> Optional[Dict]:
    """Una fracción exacta, o None para ±∞.

    Se manda numerador y denominador por separado (y no un float) para que el
    frontend pueda mostrar −3/2 y no −1.5, que es lo que se espera en el examen.
    """
    if x is None:
        return None
    f = Fraction(x)
    return {"num": f.numerator, "den": f.denominator, "valor": float(f)}


# --------------------------------------------------------------------------
# Lógica y conjuntos
# --------------------------------------------------------------------------

def forma_a_json(f: L.Form) -> Dict:
    """Árbol de la fórmula proposicional.

    El frontend lo usa para resaltar la subfórmula que se reescribió en cada
    paso, buscando la primera coincidencia en pre-orden — que es exactamente la
    semántica de `reemplazar()` en logica/formula.py.
    """
    if isinstance(f, L.Var):
        return {"tipo": "var", "nombre": f.nombre}
    if isinstance(f, L.Const):
        return {"tipo": "const", "valor": f.valor}
    if isinstance(f, L.Not):
        return {"tipo": "no", "a": forma_a_json(f.a)}
    nombres = {L.And: "y", L.Or: "o", L.Imp: "si", L.Iff: "sii"}
    return {
        "tipo": nombres[type(f)],
        "a": forma_a_json(f.a),
        "b": forma_a_json(f.b),
    }


def formula_completa(f: L.Form) -> Dict:
    """Una fórmula con sus tres representaciones: árbol, texto y LaTeX."""
    return {
        "arbol": forma_a_json(f),
        "texto": L.escribir(f),
        "latex": L.escribir_latex(f),
    }


def sexpr_a_json(e: cexpr.SExpr) -> Dict:
    """Árbol de la expresión de conjuntos."""
    if isinstance(e, cexpr.SVar):
        return {"tipo": "var", "nombre": e.nombre}
    if isinstance(e, cexpr.Universo):
        return {"tipo": "universo"}
    if isinstance(e, cexpr.Vacio):
        return {"tipo": "vacio"}
    if isinstance(e, cexpr.Comp):
        return {"tipo": "complemento", "a": sexpr_a_json(e.a)}
    nombres = {cexpr.Union: "union", cexpr.Inter: "interseccion", cexpr.Dif: "diferencia"}
    return {
        "tipo": nombres[type(e)],
        "a": sexpr_a_json(e.a),
        "b": sexpr_a_json(e.b),
    }


def expresion_completa(e: cexpr.SExpr) -> Dict:
    return {
        "arbol": sexpr_a_json(e),
        "texto": cexpr.escribir(e),
        "latex": cexpr.escribir_latex(e),
    }


def celdas_a_json(e: cexpr.SExpr, nombres: Sequence[str]) -> List[List[bool]]:
    """Qué regiones del diagrama de Venn ocupa la expresión.

    Es la misma interpretación que usa `expr.iguales()` para verificar las
    igualdades, así que el dibujo del frontend coincide exactamente con lo que
    se demostró.
    """
    celdas = cexpr.evaluar_celdas(e, list(nombres))
    return [list(c) for c in sorted(celdas)]


# --------------------------------------------------------------------------
# Funciones
# --------------------------------------------------------------------------

def intervalo_a_json(i: Intervalo) -> Dict:
    return {
        "izq": fraccion_a_json(i.izq),
        "der": fraccion_a_json(i.der),
        "izq_cerrado": i.izq_cerrado,
        "der_cerrado": i.der_cerrado,
    }


def dominio_a_json(d: Dominio) -> Dict:
    return {
        "texto": str(d),
        "intervalos": [intervalo_a_json(i) for i in d.intervalos],
        "excluidos": [fraccion_a_json(e) for e in d.excluidos],
    }


def muestrear(
    f: Callable[[float], float],
    dominio: Dominio,
    desde: float = -10.0,
    hasta: float = 10.0,
    cantidad: int = 240,
) -> List[List[Optional[float]]]:
    """Puntos (x, y) de la función, para que el frontend sólo dibuje.

    Devuelve y = None donde x cae fuera del dominio o la evaluación no existe:
    así el frontend levanta el trazo en vez de unir ramas que no van unidas
    (el salto en una asíntota, por ejemplo).
    """
    puntos: List[List[Optional[float]]] = []
    for i in range(cantidad + 1):
        # Se redondea *antes* de evaluar la pertenencia: así el punto que se
        # emite es exactamente el que se controló. Sin esto, un extremo como
        # 4/3 cae del lado equivocado por el redondeo.
        x = round(desde + (hasta - desde) * i / cantidad, 6)
        y: Optional[float] = None
        if dominio.contiene(x):
            try:
                valor = float(f(x))
                if -1e6 < valor < 1e6:
                    y = round(valor, 6)
            except (ValueError, ZeroDivisionError, OverflowError):
                y = None
        puntos.append([x, y])
    return puntos


# --------------------------------------------------------------------------
# Relaciones
# --------------------------------------------------------------------------

def orden_a_json(o: Orden) -> Dict:
    """Todo lo necesario para dibujar el diagrama de Hasse.

    `nivel` da la altura de cada nodo. Cuando el orden es el de inclusión sobre
    P(A), `bits` dice qué elementos de la base contiene cada nodo: con eso el
    frontend ubica los vértices en el cubo exacto, sin inventar un layout.
    """
    capas = niveles(o.elems, o.hasse)
    nivel = {e: i for i, capa in enumerate(capas) for e in capa}
    datos = {
        "elems": list(o.elems),
        "etiquetas": dict(o.etiquetas),
        "nivel": nivel,
        "hasse": [list(par) for par in sorted(o.hasse)],
        "relacion": [list(par) for par in sorted(o.relacion)],
        "total": o.es_total(),
        "incomparables": [list(par) for par in o.incomparables()],
    }
    if o.base is not None and o.conjuntos is not None:
        datos["base"] = list(o.base)
        datos["bits"] = {
            e: [x in o.conjuntos[e] for x in o.base] for e in o.elems
        }
    return datos


def particulares_a_json(o: Orden, B: Sequence[str]) -> Dict:
    """Elementos particulares de un subconjunto, ya calculados por `Orden`."""
    B = list(B)
    return {
        "subconjunto": B,
        "maximales": o.maximales(B),
        "minimales": o.minimales(B),
        "maximo": o.maximo(B),
        "minimo": o.minimo(B),
        "cotas_superiores": o.cotas_superiores(B),
        "cotas_inferiores": o.cotas_inferiores(B),
        "supremo": o.supremo(B),
        "infimo": o.infimo(B),
    }


def pares_a_json(pares) -> List[List[str]]:
    return [list(p) for p in sorted(pares)]


# --------------------------------------------------------------------------
# Ejercicios y exámenes
# --------------------------------------------------------------------------

def ejercicio_a_json(ej: Ejercicio, con_soluciones: bool = True) -> Dict:
    """Un ejercicio completo.

    Con `con_soluciones=False` se omite todo lo que revela la respuesta: sirve
    para el modo examen, donde la corrección la hace el servidor regenerando el
    mismo ejercicio a partir de la semilla.
    """
    datos = {
        "tema": ej.tema,
        "subtema": ej.subtema,
        "consigna": ej.consigna,
        "puntaje": ej.puntaje,
        "visual": ej.visual if con_soluciones else _visual_sin_soluciones(ej.visual),
    }
    if con_soluciones:
        datos["pasos"] = [{"titulo": p.titulo, "detalle": p.detalle} for p in ej.pasos]
        datos["respuesta"] = ej.respuesta
        datos["observacion"] = ej.observacion
        datos["verificacion"] = ej.verificacion
        datos["practica"] = ej.practica
    else:
        # El esquema de la práctica viaja sin las respuestas correctas.
        datos["practica"] = _practica_sin_respuestas(ej.practica)
    return datos


# Qué parte del payload visual se puede mostrar sin regalar la respuesta.
# Todo lo que no esté acá se omite en modo examen: la cadena de equivalencias,
# las regiones ya contadas del Venn o los elementos particulares del Hasse son
# justamente lo que hay que resolver.
_VISUAL_PUBLICO = {
    "cadena-logica": ["tipo", "inicial"],
    "derivacion": ["tipo", "premisas", "meta"],
    "cuantificadores": ["tipo", "ventana", "predicados"],
    "venn-conteo": ["tipo", "letras", "nombres", "unidad", "total"],
    "venn-elementos": ["tipo", "letras", "datos"],
    "cadena-conjuntos": ["tipo", "variables", "inicial", "final"],
    "relacion": ["tipo", "A", "pares"],
    "equivalencia": ["tipo", "A", "pares"],
    "hasse": [
        "tipo", "elems", "etiquetas", "nivel", "hasse", "relacion",
        "base", "bits", "conjunto_base",
    ],
    "dominio": ["tipo", "funcion"],
    "funcion-inversa": ["tipo", "funcion"],
    "composicion": ["tipo", "f", "g"],
}


def _visual_sin_soluciones(visual: Dict) -> Dict:
    """Deja sólo lo necesario para *presentar* el ejercicio."""
    if not visual:
        return {}
    permitidas = _VISUAL_PUBLICO.get(visual.get("tipo"))
    if permitidas is None:
        # Tipo nuevo todavía sin lista: se omite entero antes que filtrar mal.
        return {"tipo": visual.get("tipo")}
    limpio = {k: v for k, v in visual.items() if k in permitidas}
    if visual.get("tipo") == "cuantificadores":
        # Los conjuntos de verdad son parte de lo que hay que resolver.
        limpio["predicados"] = [
            {"nombre": p["nombre"], "texto": p["texto"]}
            for p in visual.get("predicados", [])
        ]
    return limpio


def _practica_sin_respuestas(practica: Dict) -> Dict:
    """Deja el formulario pero saca las claves que contienen la solución."""
    if not practica:
        return {}
    ocultas = {"correcta", "correctas", "valor", "valores", "solucion"}
    limpio: Dict = {}
    for clave, valor in practica.items():
        if clave in ocultas:
            continue
        if isinstance(valor, list):
            limpio[clave] = [
                _practica_sin_respuestas(v) if isinstance(v, dict) else v
                for v in valor
            ]
        elif isinstance(valor, dict):
            limpio[clave] = _practica_sin_respuestas(valor)
        else:
            limpio[clave] = valor
    return limpio


def examen_a_json(examen: Dict, con_soluciones: bool = True) -> Dict:
    return {
        "titulo": examen["titulo"],
        "modo": examen["modo"],
        "semilla": examen["semilla"],
        "puntaje_total": examen["puntaje_total"],
        "con_soluciones": con_soluciones,
        "ejercicios": [
            ejercicio_a_json(ej, con_soluciones) for ej in examen["ejercicios"]
        ],
    }
