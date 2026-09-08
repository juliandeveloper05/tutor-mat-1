"""Estructuras comunes a todos los generadores de ejercicios."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Paso:
    """Un paso de la resolución.

    titulo:  encabezado corto (ej. "Paso 2 — Ley de De Morgan").
    detalle: explicación completa en Markdown (puede tener varias líneas).
    """

    titulo: str
    detalle: str


@dataclass
class Ejercicio:
    """Un ejercicio con su enunciado y su resolución paso a paso."""

    tema: str
    subtema: str
    consigna: str
    pasos: List[Paso] = field(default_factory=list)
    respuesta: str = ""
    puntaje: int = 10
    # Nota pedagógica: el "por qué" del procedimiento, errores típicos, etc.
    observacion: str = ""
    # Cómo verificó la máquina que la respuesta es correcta.
    verificacion: str = ""

    def agregar(self, titulo: str, detalle: str) -> None:
        self.pasos.append(Paso(titulo, detalle))
