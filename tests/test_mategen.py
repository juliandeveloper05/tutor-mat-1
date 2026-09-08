"""Batería de verificación del generador.

La idea no es sólo que el programa no se rompa, sino que **lo que afirma sea
cierto**: cada test vuelve a comprobar la respuesta por un camino independiente
del que la produjo (tablas de verdad, fuerza bruta, evaluación numérica).

Se ejecuta con:  python3 -m unittest discover -s tests -v
"""

import random
import unittest

from mategen.conjuntos import expr as cexpr
from mategen.conjuntos import extension as cext
from mategen.conjuntos import venn as cvenn
from mategen.examen import GENERADORES, MODOS, TEMAS, generar_examen
from mategen.funciones import biyectiva as fbiy
from mategen.funciones import composicion as fcomp
from mategen.funciones import dominio as fdom
from mategen.logica import cuantificadores as lcuant
from mategen.logica import derivacion as lder
from mategen.logica import leyes as lleyes
from mategen.logica.formula import equivalentes, escribir
from mategen.relaciones import equivalencia as req
from mategen.relaciones import orden as rord
from mategen.relaciones import propiedades as rprop
from mategen.render import a_html, a_markdown, a_texto

SEMILLAS = range(60)


class TestLogica(unittest.TestCase):
    def test_simplificacion_conserva_equivalencia(self):
        for s in SEMILLAS:
            enunciado, resultado, pasos = lleyes.generar_simplificacion(random.Random(s))
            self.assertTrue(
                equivalentes(enunciado, resultado),
                f"semilla {s}: {escribir(enunciado)} no equivale a {escribir(resultado)}",
            )
            self.assertTrue(pasos, f"semilla {s}: no se aplicó ninguna ley")

    def test_cada_paso_de_la_simplificacion_es_una_equivalencia(self):
        for s in SEMILLAS:
            enunciado, _resultado, pasos = lleyes.generar_simplificacion(random.Random(s))
            anterior = enunciado
            for nombre, _a, _b, completa in pasos:
                self.assertTrue(
                    equivalentes(anterior, completa),
                    f"semilla {s}: la ley «{nombre}» no preservó la equivalencia",
                )
                anterior = completa

    def test_razonamientos_validos_y_derivacion_correcta(self):
        for s in SEMILLAS:
            premisas, meta, prueba = lder.generar_derivacion(random.Random(s))
            self.assertTrue(lder.es_valido(premisas, meta), f"semilla {s}: no es válido")
            self.assertTrue(
                lder.verificar_derivacion(prueba, premisas, meta),
                f"semilla {s}: la derivación no resiste el control renglón por renglón",
            )

    def test_valores_de_verdad_de_los_cuantificadores(self):
        """Recalcula el valor de verdad por su cuenta y lo compara con el informado."""
        for s in SEMILLAS:
            preds, items = lcuant.generar_items(random.Random(s))
            self.assertEqual(len(items), 3)
            self.assertEqual(len({i.valor for i in items}), 2, "faltan casos V y F")
            for it in items:
                cuerpo = [
                    lcuant._eval_cuerpo(it.forma, it.p, it.q, x) for x in lcuant.VENTANA
                ]
                esperado = all(cuerpo) if it.cuant == "todo" else any(cuerpo)
                self.assertEqual(
                    it.valor, esperado, f"semilla {s}: {it.enunciado} mal evaluada"
                )
                # El testigo o contraejemplo citado debe existir de verdad.
                import re

                citado = re.search(r"x = (−?-?\d+)", it.justificacion)
                if citado:
                    x = int(citado.group(1).replace("−", "-"))
                    valor_ahi = lcuant._eval_cuerpo(it.forma, it.p, it.q, x)
                    self.assertEqual(
                        valor_ahi,
                        it.valor,
                        f"semilla {s}: el ejemplo x={x} no sostiene lo que se afirma",
                    )


class TestConjuntos(unittest.TestCase):
    def test_extension_reconstruye_los_datos(self):
        for s in SEMILLAS:
            ej = cext.generar(random.Random(s))
            self.assertTrue(cext.verificar(ej), f"semilla {s}: los datos no son consistentes")

    def test_venn_suma_el_total(self):
        for s in SEMILLAS:
            ej = cvenn.generar(random.Random(s))
            self.assertTrue(cvenn.verificar(ej), f"semilla {s}: el conteo no cierra")
            for p in ej["preguntas"]:
                self.assertGreaterEqual(p["valor"], 0)

    def test_identidad_de_conjuntos(self):
        for s in SEMILLAS:
            enunciado, resultado, pasos = cexpr.generar_identidad(random.Random(s))
            self.assertTrue(
                cexpr.iguales(enunciado, resultado),
                f"semilla {s}: {cexpr.escribir(enunciado)} ≠ {cexpr.escribir(resultado)}",
            )
            anterior = enunciado
            for ley, expr in pasos:
                self.assertTrue(
                    cexpr.iguales(anterior, expr), f"semilla {s}: falla el paso «{ley}»"
                )
                anterior = expr


class TestRelaciones(unittest.TestCase):
    def test_correcciones_de_propiedades(self):
        for s in SEMILLAS:
            d = rprop.generar(random.Random(s))
            A, R = d["A"], d["R"]
            self.assertTrue(analiza(A, R | set(d["agregar_reflexiva"]), "reflexiva"))
            self.assertTrue(analiza(A, R - set(d["quitar_antisimetrica"]), "antisimetrica"))
            self.assertTrue(analiza(A, R | set(d["agregar_simetrica"]), "simetrica"))
            self.assertTrue(analiza(A, R - set(d["quitar_irreflexiva"]), "irreflexiva"))

    def test_equivalencia_y_particion(self):
        for s in SEMILLAS:
            d = req.generar(random.Random(s))
            self.assertTrue(req.verificar(d), f"semilla {s}: clases mal calculadas")

    def test_orden_es_un_orden_y_el_hasse_lo_reconstruye(self):
        for s in SEMILLAS:
            o = rord.generar_orden(random.Random(s))
            # reflexiva, antisimétrica y transitiva
            for x in o.elems:
                self.assertIn((x, x), o.relacion)
            for x in o.elems:
                for y in o.elems:
                    if x != y and (x, y) in o.relacion:
                        self.assertNotIn((y, x), o.relacion, "no es antisimétrica")
                    for z in o.elems:
                        if (x, y) in o.relacion and (y, z) in o.relacion:
                            self.assertIn((x, z), o.relacion, "no es transitiva")
            # el diagrama de Hasse debe generar exactamente el mismo orden estricto
            self.assertEqual(
                rord.clausura_transitiva(o.elems, o.hasse),
                o.estricto,
                f"semilla {s}: el diagrama de Hasse pierde información",
            )

    def test_orden_de_partes(self):
        o = rord.orden_partes(["a", "b", "c"])
        self.assertEqual(len(o.elems), 8)
        self.assertFalse(o.es_total())
        self.assertIsNotNone(o.maximo(o.elems))
        self.assertIsNotNone(o.minimo(o.elems))


class TestFunciones(unittest.TestCase):
    def test_dominio_natural(self):
        for s in range(150):
            ej = fdom.generar(random.Random(s))
            self.assertTrue(fdom.verificar(ej), f"semilla {s}: {ej['texto']} / {ej['dominio']}")

    def test_inversa(self):
        for s in range(150):
            ej = fbiy.generar(random.Random(s))
            self.assertTrue(
                fbiy.verificar(ej), f"semilla {s}: {ej['texto']} / {ej['inversa_texto']}"
            )

    def test_composicion(self):
        for s in range(150):
            ej = fcomp.generar(random.Random(s))
            self.assertTrue(fcomp.verificar(ej), f"semilla {s}: {ej['tipo']}")


class TestExamen(unittest.TestCase):
    def test_todos_los_generadores_producen_ejercicios_completos(self):
        for clave, generador in GENERADORES.items():
            for s in (1, 2, 3):
                ej = generador(random.Random(s))
                self.assertTrue(ej.consigna.strip(), f"{clave}: consigna vacía")
                self.assertTrue(ej.pasos, f"{clave}: sin resolución")
                self.assertTrue(ej.respuesta.strip(), f"{clave}: sin respuesta")
                self.assertTrue(ej.verificacion.strip(), f"{clave}: sin nota de verificación")
                for paso in ej.pasos:
                    self.assertTrue(paso.detalle.strip(), f"{clave}: paso vacío")

    def test_modos_y_temas(self):
        for modo in MODOS:
            ex = generar_examen(modo=modo, semilla=11)
            self.assertEqual(len(ex["ejercicios"]), len(MODOS[modo]))
        for tema in TEMAS:
            ex = generar_examen(semilla=11, tema=tema)
            self.assertEqual(len(ex["ejercicios"]), len(TEMAS[tema]))

    def test_el_integrador_suma_cien_puntos(self):
        self.assertEqual(generar_examen("integrador", semilla=1)["puntaje_total"], 100)
        self.assertEqual(generar_examen("parcial1", semilla=1)["puntaje_total"], 100)

    def test_misma_semilla_mismo_examen(self):
        a = a_markdown(generar_examen("integrador", semilla=123))
        b = a_markdown(generar_examen("integrador", semilla=123))
        c = a_markdown(generar_examen("integrador", semilla=124))
        self.assertEqual(a, b, "la semilla no reproduce el mismo examen")
        self.assertNotEqual(a, c, "semillas distintas dan el mismo examen")

    def test_los_tres_formatos_salen_sin_errores(self):
        ex = generar_examen("completo", semilla=9)
        for texto in (a_markdown(ex), a_texto(ex), a_html(ex)):
            self.assertGreater(len(texto), 5000)
        html = a_html(ex)
        self.assertIn("<!doctype html>", html)
        self.assertEqual(html.count("<pre"), html.count("</pre>"))


def analiza(A, R, propiedad):
    return rprop.analizar(A, R)[propiedad][0]


if __name__ == "__main__":
    unittest.main()
