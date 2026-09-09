# Generador de Integradores — Matemática I

### → **[tutor-mat-1.vercel.app](https://tutor-mat-1.vercel.app)**

Generador automático de exámenes integradores de **Matemática I** (Tecnicatura /
Licenciatura en Informática, UNQ), con la **resolución explicada paso a paso**
y los diagramas dibujados.

Los ejercicios se arman siguiendo el estilo y la dificultad de los trabajos
prácticos y de los parciales de la cátedra: Lógica, Conjuntos, Relaciones y
Funciones.

Se puede usar de tres formas: desde la web, por línea de comandos, o pegándole
a la API.

| | |
|---|---|
| Practicar con los diagramas | [tutor-mat-1.vercel.app](https://tutor-mat-1.vercel.app) |
| Un integrador ya armado | [/examen/2026?modo=integrador](https://tutor-mat-1.vercel.app/examen/2026?modo=integrador) |
| Rendirlo sin resolución | […&soluciones=false](https://tutor-mat-1.vercel.app/examen/2026?modo=integrador&soluciones=false) |
| Generar en papel | `python3 integrador.py -f html -o examen.html` |

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

## La aplicación web

Los ejercicios dibujados, con la resolución que se va revelando paso a paso y la
posibilidad de contestar y corregirse.

```bash
pip install -r requirements.txt
npm install
npm run dev          # levanta Next en :3000 y el backend Python en :8000
```

| Qué | Dónde |
|---|---|
| Elegir modo, unidad y semilla | `/` |
| Recorrer un examen | `/examen/2026?modo=integrador` |
| Rendirlo sin resolución | `/examen/2026?modo=integrador&soluciones=false` |

**El visual acompaña al stepper, no se adelanta.** El diagrama de Venn arranca
vacío y las regiones se completan recién en el paso donde se deducen; la cadena
de equivalencias no muestra el nombre de la ley del paso que todavía no abriste;
la tabla de elementos particulares del Hasse aparece al final. Sin eso el panel
de "Contestá vos" sería copiar la respuesta que está al lado.

Las visualizaciones:

- **Diagrama de Venn** en SVG, con las ocho regiones dibujadas de forma exacta
  (intersección por `clipPath` anidado y resta por máscara, no aproximada a ojo).
- **Diagrama de Hasse en 3D** con Three.js. Cuando el orden es la inclusión
  sobre P(A) con #A = 3, los vértices van en las coordenadas exactas del cubo y
  el conjunto se rota para que la diagonal (1,1,1) —la dirección en la que crece
  la inclusión— quede vertical: así es a la vez el cubo real y un Hasse que se
  lee de abajo hacia arriba. Se gira con el mouse.
- **Recta real** con los extremos abiertos y cerrados como corresponde, y los
  puntos excluidos marcados aparte.
- **Cadena de equivalencias** con el detalle de qué se reescribió en cada paso.
- **Gráficos de funciones** con los puntos muestreados desde Python: donde la
  función no está definida se levanta el trazo en vez de unir ramas que no van
  unidas.

El 3D se usa **sólo** para los diagramas de Hasse, que es donde aporta; el resto
es SVG, que se lee mejor. Si no hay WebGL, el Hasse cae a un diagrama por
niveles en texto que dice lo mismo.

## API

Además de la CLI, el generador se expone por HTTP para la aplicación web. La API
es una capa fina: toda la matemática vive en el paquete `mategen`.

```bash
pip install -r requirements.txt
uvicorn api.index:app --reload        # http://127.0.0.1:8000/docs
```

| Endpoint | Qué hace |
|---|---|
| `GET /api/tipos` | modos, temas y tipos de ejercicio disponibles |
| `GET /api/examen?semilla=2026&modo=integrador` | genera un examen en JSON |
| `GET /api/examen?...&soluciones=false` | modo examen: sin resolución ni respuestas |
| `POST /api/corregir` | corrige un examen a partir de su semilla |

Cada ejercicio viaja con un campo `visual` que trae los datos para dibujarlo (las
regiones del Venn, las aristas del diagrama de Hasse, los intervalos del dominio,
los puntos ya muestreados de cada función) y un campo `practica` con el esquema
de la respuesta.

**No hay base de datos.** Como el generador es determinístico, para corregir
alcanza con volver a generar el mismo examen a partir de la semilla:

```bash
curl -X POST localhost:8000/api/corregir -H 'Content-Type: application/json' \
  -d '{"semilla": 2026, "modo": "integrador", "respuestas": [...]}'
```

En modo examen el servidor además **filtra** el payload visual con una lista
blanca por tipo de ejercicio: sin eso, las regiones ya contadas del Venn o los
elementos particulares del Hasse regalarían la respuesta.

## Deploy

Está desplegado en **[tutor-mat-1.vercel.app](https://tutor-mat-1.vercel.app)**
y cada push a `main` lo actualiza solo. No hay variables de entorno ni comando
de build que configurar.

Para levantar otra copia: en Vercel, **Add New → Project → Import** el
repositorio y **Deploy**; el framework se detecta solo.

Cómo está armado:

- `api/index.py` se despliega como función serverless de Python. `vercel.json`
  usa `includeFiles` para que el paquete `mategen` viaje dentro de la función,
  que si no quedaría afuera del bundle.
- El rewrite de `vercel.json` manda `/api/*` a esa función.
- `next.config.ts` desactiva su propio rewrite cuando detecta la variable
  `VERCEL`, así en producción no compite con el anterior. Fuera de Vercel —
  tanto `next dev` como `next start` en tu máquina— apunta al uvicorn local.

Una vez importado, cada push a `main` despliega solo.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Los tests no comprueban que el programa "no se rompa": recalculan cada respuesta
de forma independiente sobre decenas de semillas distintas.

## Estructura

```
integrador.py              CLI
api/index.py               API HTTP (FastAPI)
app/                       aplicación Next.js (TypeScript)
  page.tsx                 elegir qué practicar
  examen/[semilla]/        recorrer el examen
  componentes/visuales/    Venn, Hasse 3D, recta real, cadena, curvas
  lib/tipos.ts             tipos espejo del JSON de mategen/serial.py
mategen/
  examen.py                arma los exámenes y redacta cada ejercicio
  serial.py                serialización a JSON para el frontend
  correccion.py            corrección de las respuestas del modo práctica
  render.py                salida en Markdown, texto y HTML
  ejercicio.py             estructura común (consigna, pasos, respuesta, visual)
  logica/                  fórmulas, leyes, derivaciones, cuantificadores
  conjuntos/               expresiones, extensión, Venn
  relaciones/              propiedades, equivalencia, orden
  funciones/               dominio, biyectividad, composición
tests/                     batería de verificación
```
