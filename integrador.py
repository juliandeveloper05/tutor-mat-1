#!/usr/bin/env python3
"""Generador de exámenes integradores de Matemática I (TUPI — UNQ).

Uso rápido:

    python3 integrador.py                          # integrador completo con resolución
    python3 integrador.py --tema logica            # sólo lógica
    python3 integrador.py --modo parcial1          # simulacro de primer parcial
    python3 integrador.py --sin-soluciones         # para rendir en serio y corregir después
    python3 integrador.py --formato html -o examen.html
    python3 integrador.py --tipo dominio -n 10     # 10 ejercicios de dominio natural

No requiere instalar nada: sólo Python 3.8 o superior.
"""

import argparse
import random
import sys
from pathlib import Path

from mategen.examen import GENERADORES, MODOS, TEMAS, generar_examen
from mategen.render import a_html, a_markdown, a_texto


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="integrador.py",
        description="Genera exámenes integradores de Matemática I con resolución explicada.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Modos disponibles: " + ", ".join(MODOS) + "\n"
            "Temas disponibles: " + ", ".join(TEMAS) + "\n"
            "Tipos de ejercicio: " + ", ".join(GENERADORES)
        ),
    )
    p.add_argument("--modo", default="integrador", choices=sorted(MODOS),
                   help="qué examen armar (por defecto: integrador)")
    p.add_argument("--tema", choices=sorted(TEMAS),
                   help="practicar una sola unidad")
    p.add_argument("--tipo", choices=sorted(GENERADORES),
                   help="generar un único tipo de ejercicio")
    p.add_argument("-n", "--cantidad", type=int, default=1,
                   help="cuántos ejercicios generar cuando se usa --tipo")
    p.add_argument("-s", "--semilla", type=int,
                   help="semilla para reproducir exactamente el mismo examen")
    p.add_argument("-f", "--formato", default="md", choices=["md", "html", "txt"],
                   help="formato de salida (por defecto: md)")
    p.add_argument("-o", "--salida", help="archivo donde escribir (por defecto: pantalla)")
    p.add_argument("--sin-soluciones", action="store_true",
                   help="imprimir sólo los enunciados")
    p.add_argument("--soluciones-aparte", action="store_true",
                   help="poner todas las resoluciones al final, después de los enunciados")
    p.add_argument("--listar", action="store_true",
                   help="mostrar los modos, temas y tipos disponibles y salir")
    return p


def listar() -> None:
    print("Modos (--modo):")
    for modo, claves in MODOS.items():
        print(f"  {modo:12s} {len(claves)} ejercicios: {', '.join(claves)}")
    print("\nTemas (--tema):")
    for tema, claves in TEMAS.items():
        print(f"  {tema:12s} {', '.join(claves)}")
    print("\nTipos sueltos (--tipo):")
    for clave in GENERADORES:
        print(f"  {clave}")


def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)

    if args.listar:
        listar()
        return 0

    if args.tipo:
        semilla = args.semilla if args.semilla is not None else random.randrange(1, 10 ** 6)
        rng = random.Random(semilla)
        ejercicios = [GENERADORES[args.tipo](rng) for _ in range(max(1, args.cantidad))]
        examen = {
            "titulo": f"Práctica de {ejercicios[0].subtema}",
            "modo": args.tipo,
            "semilla": semilla,
            "ejercicios": ejercicios,
            "puntaje_total": sum(e.puntaje for e in ejercicios),
        }
    else:
        examen = generar_examen(modo=args.modo, semilla=args.semilla, tema=args.tema)

    con_soluciones = not args.sin_soluciones
    if args.formato == "html":
        salida = a_html(examen, con_soluciones, args.soluciones_aparte)
    elif args.formato == "txt":
        salida = a_texto(examen, con_soluciones)
    else:
        salida = a_markdown(examen, con_soluciones, args.soluciones_aparte)

    if args.salida:
        destino = Path(args.salida)
        destino.write_text(salida, encoding="utf-8")
        print(f"Listo: {destino}  (semilla {examen['semilla']})", file=sys.stderr)
    else:
        print(salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
