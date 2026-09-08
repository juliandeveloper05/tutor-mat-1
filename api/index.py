"""API HTTP del generador.

Es una capa fina: recibe parámetros, llama al paquete `mategen` y devuelve JSON.
Toda la matemática (y la corrección) vive en el paquete, que es lo que los tests
verifican.

Corre igual en dos lados:

  * local:  uvicorn api.index:app --reload   (http://127.0.0.1:8000)
  * Vercel: como función serverless de Python, con el rewrite de vercel.json

Para corregir no hace falta guardar nada: como el generador es determinístico,
el servidor vuelve a generar el mismo examen a partir de la semilla.
"""

import sys
from pathlib import Path
from typing import Any, List, Optional

# Permite importar `mategen` cuando el archivo se ejecuta como función aislada.
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi import FastAPI, HTTPException, Query  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from mategen.correccion import corregir_examen  # noqa: E402
from mategen.examen import GENERADORES, MODOS, TEMAS, generar  # noqa: E402
from mategen.serial import examen_a_json  # noqa: E402

app = FastAPI(
    title="Generador de Integradores — Matemática I",
    description="Genera y corrige ejercicios de Matemática I (TUPI/UNQ).",
    version="1.0.0",
)

# En desarrollo el frontend corre en otro puerto.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class Correccion(BaseModel):
    semilla: int
    modo: str = "integrador"
    tema: Optional[str] = None
    tipo: Optional[str] = None
    cantidad: int = 1
    respuestas: List[Any] = Field(default_factory=list)


def _catalogo():
    return {
        "modos": {
            nombre: {"ejercicios": claves, "cantidad": len(claves)}
            for nombre, claves in MODOS.items()
        },
        "temas": {nombre: claves for nombre, claves in TEMAS.items()},
        "tipos": list(GENERADORES),
    }


def _examen(modo, tema, tipo, cantidad, semilla, soluciones):
    try:
        examen = generar(
            modo=modo, semilla=semilla, tema=tema, tipo=tipo, cantidad=cantidad
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return examen_a_json(examen, con_soluciones=soluciones)


def _corregir(datos: Correccion):
    try:
        examen = generar(
            modo=datos.modo,
            semilla=datos.semilla,
            tema=datos.tema,
            tipo=datos.tipo,
            cantidad=datos.cantidad,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return corregir_examen(examen, datos.respuestas)


# Las rutas se registran con y sin el prefijo /api para que el mismo archivo
# funcione detrás del rewrite de Vercel y con uvicorn en local.
for prefijo in ("/api", ""):

    @app.get(f"{prefijo}/tipos", tags=["catálogo"])
    def tipos():
        """Modos, temas y tipos de ejercicio disponibles."""
        return _catalogo()

    @app.get(f"{prefijo}/examen", tags=["examen"])
    def examen(
        modo: str = Query("integrador", description="integrador, parcial1, completo, express"),
        tema: Optional[str] = Query(None, description="logica, conjuntos, relaciones, funciones"),
        tipo: Optional[str] = Query(None, description="un tipo suelto de ejercicio"),
        cantidad: int = Query(1, ge=1, le=20, description="cuántos, si se pidió un tipo"),
        semilla: Optional[int] = Query(None, description="para reproducir el mismo examen"),
        soluciones: bool = Query(True, description="false para el modo examen"),
    ):
        """Genera un examen. Sin semilla, elige una y la devuelve en la respuesta."""
        return _examen(modo, tema, tipo, cantidad, semilla, soluciones)

    @app.post(f"{prefijo}/corregir", tags=["examen"])
    def corregir(datos: Correccion):
        """Corrige un examen regenerándolo a partir de su semilla."""
        return _corregir(datos)


@app.get("/", include_in_schema=False)
def raiz():
    return {
        "nombre": "Generador de Integradores — Matemática I",
        "endpoints": ["/api/tipos", "/api/examen", "/api/corregir"],
        **_catalogo(),
    }
