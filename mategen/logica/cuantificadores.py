"""Cuantificadores y conjuntos de verdad sobre el universo U = Z.

Regla de oro del módulo: sólo se propone una proposición cuantificada si el
programa puede justificarla de manera *completa*.

  * Si resulta falsa, se exhibe el contraejemplo de menor módulo.
  * Si resulta verdadera y es existencial, se exhibe el testigo.
  * Si resulta verdadera y es universal, se exige que el antecedente tenga
    conjunto de verdad finito, de modo que la verificación caso por caso sea una
    demostración y no una inspección parcial.

Cualquier candidata que no encaje en esos casos se descarta y se genera otra.
"""

import random
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

# Ventana de exploración. Todos los predicados del banco son "estables" fuera de
# ella (ecuaciones con raíces chicas, desigualdades y condiciones de paridad),
# así que alcanza para decidir el valor de verdad.
VENTANA = range(-120, 121)


@dataclass
class Predicado:
    nombre: str
    texto: str
    func: Callable[[int], bool]
    finito: bool
    descripcion_verdad: str

    def conjunto_verdad(self) -> List[int]:
        return [x for x in VENTANA if self.func(x)]

    def verdad_texto(self) -> str:
        if self.finito:
            valores = self.conjunto_verdad()
            if not valores:
                return "∅"
            return "{" + ", ".join(str(v) for v in valores) + "}"
        return self.descripcion_verdad


BANCO: List[Predicado] = [
    Predicado("", "x ≥ 0", lambda x: x >= 0, False, "{x ∈ Z : x ≥ 0}"),
    Predicado("", "x < 0", lambda x: x < 0, False, "{x ∈ Z : x < 0}"),
    Predicado("", "x² = 9", lambda x: x * x == 9, True, ""),
    Predicado("", "x² − 16 = 0", lambda x: x * x - 16 == 0, True, ""),
    Predicado("", "2x + 1 = 5", lambda x: 2 * x + 1 == 5, True, ""),
    Predicado("", "2x − 6 = 2", lambda x: 2 * x - 6 == 2, True, ""),
    Predicado("", "x + 3 = 0", lambda x: x + 3 == 0, True, ""),
    Predicado("", "x³ = 8", lambda x: x ** 3 == 8, True, ""),
    Predicado("", "x² + 1 = 0", lambda x: x * x + 1 == 0, True, ""),
    Predicado("", "|x| < 3", lambda x: abs(x) < 3, True, ""),
    Predicado("", "|x| ≤ 4", lambda x: abs(x) <= 4, True, ""),
    Predicado("", "x es par", lambda x: x % 2 == 0, False, "{x ∈ Z : x es par}"),
    Predicado("", "x es impar", lambda x: x % 2 != 0, False, "{x ∈ Z : x es impar}"),
    Predicado("", "x es múltiplo de 3", lambda x: x % 3 == 0, False, "{x ∈ Z : 3 | x}"),
    Predicado("", "x² > 4", lambda x: x * x > 4, False, "{x ∈ Z : x < −2 ∨ x > 2}"),
    Predicado("", "x ≤ 1", lambda x: x <= 1, False, "{x ∈ Z : x ≤ 1}"),
]


@dataclass
class ItemCuantificado:
    enunciado: str          # p.ej. "∀x: [p(x) → q(x)]"
    valor: bool
    justificacion: str      # texto completo, con contraejemplo o verificación
    # Datos estructurados, para poder recalcular el valor de verdad de forma
    # independiente (los usa la batería de tests).
    cuant: str = ""         # "todo" | "existe"
    forma: str = ""         # "imp" | "imp_neg" | "and" | "or_neg"
    p: "Predicado" = None
    q: "Predicado" = None


def _eval_cuerpo(forma: str, p: Predicado, q: Predicado, x: int) -> bool:
    if forma == "imp":
        return (not p.func(x)) or q.func(x)
    if forma == "imp_neg":
        return (not p.func(x)) or (not q.func(x))
    if forma == "and":
        return p.func(x) and q.func(x)
    if forma == "or_neg":
        return p.func(x) or (not q.func(x))
    if forma == "iff":
        return p.func(x) == q.func(x)
    raise ValueError(forma)


_CUERPO_TEXTO = {
    "imp": "{p}(x) → {q}(x)",
    "imp_neg": "{p}(x) → ¬{q}(x)",
    "and": "{p}(x) ∧ {q}(x)",
    "or_neg": "{p}(x) ∨ ¬{q}(x)",
    "iff": "{p}(x) ↔ {q}(x)",
}


def _construir_item(
    cuant: str, forma: str, p: Predicado, q: Predicado
) -> Optional[ItemCuantificado]:
    cuerpo = _CUERPO_TEXTO[forma].format(p=p.nombre, q=q.nombre)
    enunciado = f"{'∀x: [' if cuant == 'todo' else '∃x / ['}{cuerpo}]"
    valores = [(x, _eval_cuerpo(forma, p, q, x)) for x in VENTANA]
    por_modulo = sorted(valores, key=lambda t: (abs(t[0]), t[0]))

    if cuant == "todo":
        contra = next((x for x, v in por_modulo if not v), None)
        if contra is not None:
            just = (
                f"**Falsa.** Contraejemplo: x = {contra}. "
                f"Ahí {p.nombre}(x) es {'V' if p.func(contra) else 'F'} "
                f"(porque {p.texto.replace('x', f'({contra})')} es "
                f"{'verdadero' if p.func(contra) else 'falso'}) y "
                f"{q.nombre}(x) es {'V' if q.func(contra) else 'F'}, "
                f"de modo que el cuerpo del cuantificador resulta F. "
                f"Un solo contraejemplo alcanza para refutar un ∀."
            )
            return ItemCuantificado(enunciado, False, just, cuant, forma, p, q)
        # Verdadera: sólo se acepta si el antecedente es finito (prueba completa).
        if forma in ("imp", "imp_neg") and p.finito:
            soporte = p.conjunto_verdad()
            if not soporte:
                just = (
                    f"**Verdadera.** El conjunto de verdad de {p.nombre}(x) es ∅: no hay "
                    f"ningún entero con {p.texto}. Un condicional con antecedente falso es "
                    f"verdadero para todo x, así que la proposición es V por vacuidad."
                )
            else:
                detalles = ", ".join(
                    f"x = {x} (allí {q.nombre}(x) es "
                    f"{'V' if q.func(x) else 'F'})"
                    for x in soporte
                )
                just = (
                    f"**Verdadera.** El conjunto de verdad de {p.nombre}(x) es "
                    f"{p.verdad_texto()}, que es finito. Para todo x fuera de ese conjunto "
                    f"el antecedente es falso y el condicional es verdadero. Queda verificar "
                    f"únicamente los elementos del conjunto: {detalles}. "
                    f"En todos ellos el consecuente es verdadero, luego la implicación vale "
                    f"para todo entero."
                )
            return ItemCuantificado(enunciado, True, just, cuant, forma, p, q)
        return None  # no se puede justificar de forma completa: se descarta

    # Existencial
    testigo = next((x for x, v in por_modulo if v), None)
    if testigo is not None:
        just = (
            f"**Verdadera.** Testigo: x = {testigo}. Allí {p.nombre}(x) es "
            f"{'V' if p.func(testigo) else 'F'} y {q.nombre}(x) es "
            f"{'V' if q.func(testigo) else 'F'}, con lo cual el cuerpo del cuantificador "
            f"resulta V. Para un ∃ basta exhibir un elemento del universo que lo cumpla."
        )
        return ItemCuantificado(enunciado, True, just, cuant, forma, p, q)

    # Falsa: se acepta sólo si algún predicado finito acota la búsqueda.
    if forma == "and" and (p.finito or q.finito):
        finito = p if p.finito else q
        otro = q if p.finito else p
        soporte = finito.conjunto_verdad()
        if not soporte:
            just = (
                f"**Falsa.** El conjunto de verdad de {finito.nombre}(x) es ∅, así que la "
                f"conjunción {finito.nombre}(x) ∧ {otro.nombre}(x) es falsa para todo entero."
            )
        else:
            detalles = ", ".join(
                f"x = {x} (allí {otro.nombre}(x) es F)" for x in soporte
            )
            just = (
                f"**Falsa.** Para que la conjunción sea verdadera hace falta, en particular, "
                f"que valga {finito.nombre}(x), y su conjunto de verdad es "
                f"{finito.verdad_texto()}. Basta entonces revisar esos valores: {detalles}. "
                f"En ninguno se cumple {otro.nombre}(x), luego no existe tal entero."
            )
        return ItemCuantificado(enunciado, False, just, cuant, forma, p, q)
    return None


def generar_items(rng: random.Random, cantidad: int = 3) -> Tuple[List[Predicado], List[ItemCuantificado]]:
    """Elige 3 predicados y arma `cantidad` proposiciones cuantificadas.

    Se asegura que haya al menos una verdadera y una falsa (como en el parcial).
    """
    for _ in range(400):
        elegidos = rng.sample(BANCO, 3)
        preds = []
        for nombre, base in zip(["p", "q", "r"], elegidos):
            preds.append(
                Predicado(nombre, base.texto, base.func, base.finito, base.descripcion_verdad)
            )
        # Formas que efectivamente toma la cátedra: el universal con condicional
        # y el existencial con conjunción o disyunción.
        combinaciones = [
            (c, f, a, b)
            for c, formas in (("todo", ("imp", "imp_neg")), ("existe", ("and", "or_neg")))
            for f in formas
            for a in range(3)
            for b in range(3)
            if a != b
        ]
        rng.shuffle(combinaciones)
        items: List[ItemCuantificado] = []
        vistos = set()
        for c, f, a, b in combinaciones:
            item = _construir_item(c, f, preds[a], preds[b])
            if item is None or item.enunciado in vistos:
                continue
            vistos.add(item.enunciado)
            items.append(item)
            if len(items) == cantidad:
                break
        if len(items) == cantidad and len({i.valor for i in items}) == 2:
            return preds, items
    raise RuntimeError("No se pudieron generar los ítems de cuantificadores")
