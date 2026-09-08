# Generador de Integradores — Matemática I

Generador automático de exámenes integradores de **Matemática I** (Tecnicatura /
Licenciatura en Informática, UNQ), con la **resolución explicada paso a paso**.

Los ejercicios se arman siguiendo el estilo y la dificultad de los trabajos
prácticos y de los parciales de la cátedra: Lógica, Conjuntos, Relaciones y
Funciones.

## Empezar (no hay nada que instalar)

Sólo hace falta Python 3.8 o superior.

```bash
python3 integrador.py                     # integrador completo, con resolución
python3 integrador.py --sin-soluciones    # sólo los enunciados, para rendir en serio
python3 integrador.py --tema logica       # practicar una sola unidad
python3 integrador.py --modo parcial1     # simulacro del primer parcial (40/30/30)
python3 integrador.py --tipo dominio -n 10   # 10 ejercicios de dominio natural
python3 integrador.py -f html -o examen.html # versión para leer en el navegador o imprimir
```

Para ver todas las opciones: `python3 integrador.py --help` o `--listar`.

### Cómo estudiar con esto

1. Generar un examen **sin soluciones** y anotarse la semilla que imprime:
   `python3 integrador.py --sin-soluciones -s 2026 -o parcial.md`
2. Resolverlo en papel, con tiempo (2 horas, como el parcial).
3. Generar **el mismo examen** con la resolución usando la misma semilla:
   `python3 integrador.py -s 2026`

La semilla garantiza que se obtenga exactamente el mismo examen, así que se puede
rendir primero y corregir después.

## Qué genera

| Unidad | Tipos de ejercicio |
|---|---|
| **Lógica** | Simplificación con leyes lógicas · Validez de un razonamiento por derivaciones · Cuantificadores y conjuntos de verdad |
| **Conjuntos** | Determinar conjuntos por extensión · Problemas de conteo con diagrama de Venn · Demostración de igualdades con propiedades |
| **Relaciones** | Propiedades (reflexiva, simétrica, antisimétrica, transitiva) y cómo corregirlas · Clases de equivalencia y conjunto cociente · Orden, diagrama de Hasse y elementos particulares |
| **Funciones** | Dominio natural · Biyectividad, redefinición y función inversa · Composición y su dominio |
| **Integrador** | La inclusión ⊆ como relación de orden en P(A) — cruza Conjuntos con Relaciones |

Modos disponibles: `integrador` (las cuatro unidades, 100 puntos), `parcial1`
(formato exacto del primer parcial: Lógica 40 % / Conjuntos 30 % / Relaciones
30 %), `completo` (uno de cada tipo) y `express` (cuatro ejercicios cortos).

## Por qué se puede confiar en las respuestas

Las resoluciones no están escritas a mano ni sacadas de una plantilla: **se
calculan**, y después se vuelven a comprobar por un camino independiente.

- **Lógica.** La equivalencia entre el enunciado y la forma simplificada se
  verifica con la tabla de verdad completa, y *cada paso intermedio* también. Los
  razonamientos se generan junto con su derivación, hallada por un encadenador
  que sólo usa reglas de inferencia; además se controla renglón por renglón que
  cada línea se siga semánticamente de las que cita.
- **Cuantificadores.** Sólo se propone una proposición cuando el programa puede
  justificarla de forma completa: contraejemplo si es falsa, testigo si es
  existencial y verdadera, o verificación finita exhaustiva si es universal y
  verdadera.
- **Conjuntos.** Las igualdades se comprueban interpretando ambos miembros en el
  álgebra de Boole libre (qué regiones del diagrama de Venn ocupa cada uno). Los
  problemas de conteo se construyen desde las regiones, así que son consistentes
  por construcción, y se controla que las 8 regiones sumen el total.
- **Relaciones.** Las propiedades se deciden recorriendo todos los pares y todas
  las cadenas; el diagrama de Hasse se controla verificando que su clausura
  transitiva devuelve el orden original.
- **Funciones.** Los dominios, las inversas y las composiciones se validan
  numéricamente evaluando las fórmulas en cientos de puntos.

Cada ejercicio del examen termina con una línea que dice cómo fue verificado.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Los tests no comprueban que el programa "no se rompa": recalculan cada respuesta
de forma independiente sobre decenas de semillas distintas.

## Estructura

```
integrador.py              CLI
mategen/
  examen.py                arma los exámenes y redacta cada ejercicio
  render.py                salida en Markdown, texto y HTML
  ejercicio.py             estructura común (consigna, pasos, respuesta)
  logica/                  fórmulas, leyes, derivaciones, cuantificadores
  conjuntos/               expresiones, extensión, Venn
  relaciones/              propiedades, equivalencia, orden
  funciones/               dominio, biyectividad, composición
tests/                     batería de verificación
```
