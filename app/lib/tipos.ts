/**
 * Tipos espejo del JSON que produce `mategen/serial.py`.
 *
 * Se escriben a mano y a propósito: son pocos, cambian poco, y tenerlos
 * explícitos hace que TypeScript avise si el backend deja de mandar algo que la
 * interfaz usa.
 */

export interface Fraccion {
  num: number;
  den: number;
  valor: number;
}

// --- Lógica ---------------------------------------------------------------

export type NodoFormula =
  | { tipo: "var"; nombre: string }
  | { tipo: "const"; valor: boolean }
  | { tipo: "no"; a: NodoFormula }
  | { tipo: "y" | "o" | "si" | "sii"; a: NodoFormula; b: NodoFormula };

export interface Formula {
  arbol: NodoFormula;
  texto: string;
  latex: string;
}

// --- Conjuntos ------------------------------------------------------------

export type NodoConjunto =
  | { tipo: "var"; nombre: string }
  | { tipo: "universo" }
  | { tipo: "vacio" }
  | { tipo: "complemento"; a: NodoConjunto }
  | { tipo: "union" | "interseccion" | "diferencia"; a: NodoConjunto; b: NodoConjunto };

export interface Expresion {
  arbol: NodoConjunto;
  texto: string;
  latex: string;
}

// --- Funciones ------------------------------------------------------------

export interface Intervalo {
  izq: Fraccion | null;
  der: Fraccion | null;
  izq_cerrado: boolean;
  der_cerrado: boolean;
}

export interface DominioJSON {
  texto: string;
  intervalos: Intervalo[];
  excluidos: Fraccion[];
}

/** Un punto de la curva. `y` es null donde la función no está definida. */
export type Muestra = [number, number | null];

// --- Payloads visuales ----------------------------------------------------

export interface RegionesVenn {
  a: number;
  b: number;
  c: number;
  ab: number;
  ac: number;
  bc: number;
  abc: number;
  afuera: number;
}

export interface VisualCadenaLogica {
  tipo: "cadena-logica";
  inicial: Formula;
  final?: Formula;
  pasos?: { ley: string; antes: Formula; despues: Formula; completa: Formula }[];
}

export interface VisualDerivacion {
  tipo: "derivacion";
  premisas: Formula[];
  meta: Formula;
  renglones?: { n: number; formula: Formula; regla: string; refs: number[] }[];
}

export interface VisualCuantificadores {
  tipo: "cuantificadores";
  ventana: number[];
  predicados: {
    nombre: string;
    texto: string;
    finito?: boolean;
    conjunto_verdad?: string;
    puntos?: number[];
    todos_los_puntos?: number[] | null;
  }[];
  items?: {
    enunciado: string;
    valor: boolean;
    cuant: string;
    forma: string;
    predicados: string[];
    puntos: number[];
  }[];
}

export interface VisualVennConteo {
  tipo: "venn-conteo";
  letras: string[];
  nombres: string[];
  unidad: string;
  total: number;
  regiones?: RegionesVenn;
  resaltados?: { pregunta: number; regiones: string[] }[];
}

export interface VisualVennElementos {
  tipo: "venn-elementos";
  letras: string[];
  datos: { clave: string; valor: string }[];
  conjuntos?: Record<string, number[]>;
  regiones?: Record<string, number[]>;
}

export interface VisualCadenaConjuntos {
  tipo: "cadena-conjuntos";
  variables: string[];
  inicial: Expresion;
  final: Expresion;
  pasos?: { ley: string; completa: Expresion }[];
  celdas_inicial?: boolean[][];
  celdas_final?: boolean[][];
}

export interface Particulares {
  subconjunto: string[];
  maximales: string[];
  minimales: string[];
  maximo: string | null;
  minimo: string | null;
  cotas_superiores: string[];
  cotas_inferiores: string[];
  supremo: string | null;
  infimo: string | null;
}

export interface VisualRelacion {
  tipo: "relacion";
  A: string[];
  pares: [string, string][];
  propiedades?: Record<string, { vale: boolean; testigos: unknown[] }>;
  correcciones?: Record<string, [string, string][]>;
}

export interface VisualEquivalencia {
  tipo: "equivalencia";
  A: string[];
  pares: [string, string][];
  propiedades?: Record<string, { vale: boolean; testigos: unknown[] }>;
  es_equivalencia?: boolean;
  propiedad_rota?: string | null;
  clases?: Record<string, string[]> | null;
  cociente?: string[][] | null;
  particion?: string[][];
}

export interface VisualHasse {
  tipo: "hasse";
  elems: string[];
  etiquetas: Record<string, string>;
  nivel: Record<string, number>;
  hasse: [string, string][];
  relacion: [string, string][];
  total?: boolean;
  incomparables?: [string, string][];
  /** Sólo en el orden por inclusión: da las coordenadas exactas del cubo. */
  base?: string[];
  bits?: Record<string, boolean[]>;
  conjunto_base?: string[];
  particulares?: Particulares;
  consigna_subconjunto?: string;
}

export interface VisualDominio {
  tipo: "dominio";
  funcion: string;
  dominio?: DominioJSON;
  muestras?: Muestra[];
}

export interface VisualFuncionInversa {
  tipo: "funcion-inversa";
  funcion: string;
  inversa?: string;
  dominio_natural?: DominioJSON;
  dominio?: DominioJSON;
  imagen?: DominioJSON;
  muestras_f?: Muestra[];
  muestras_inversa?: Muestra[];
  inyectiva?: boolean;
  sobreyectiva?: boolean;
}

export interface VisualComposicion {
  tipo: "composicion";
  f: string;
  g: string;
  gf?: { texto: string; dominio: DominioJSON; muestras: Muestra[] };
  fg?: { texto: string; dominio: DominioJSON; muestras: Muestra[] };
}

export type Visual =
  | VisualCadenaLogica
  | VisualDerivacion
  | VisualCuantificadores
  | VisualVennConteo
  | VisualVennElementos
  | VisualCadenaConjuntos
  | VisualRelacion
  | VisualEquivalencia
  | VisualHasse
  | VisualDominio
  | VisualFuncionInversa
  | VisualComposicion;

// --- Práctica -------------------------------------------------------------

export interface OpcionMultiple {
  opciones: string[];
  correcta?: number;
}

export type Practica =
  | ({ tipo: "opcion-multiple"; pregunta: string } & OpcionMultiple)
  | { tipo: "verdadero-falso"; items: { enunciado: string; correcta?: boolean }[] }
  | { tipo: "numerica"; items: { texto: string; expresion: string; valor?: number }[] }
  | ({ tipo: "nombrar-ley" | "nombrar-regla" } & {
      items: ({ antes?: Formula | Expresion | null; despues?: Formula | Expresion; n?: number; formula?: Formula; refs?: number[] } & OpcionMultiple)[];
    })
  | { tipo: "propiedades"; propiedades: string[]; correctas?: Record<string, boolean> }
  | { tipo: "si-no"; pregunta: string; correcta?: boolean }
  | {
      tipo: "elementos-particulares";
      subconjunto: string[];
      etiquetas: Record<string, string>;
      opciones: string[];
      preguntas: { clave: string; texto: string; correcta?: string | null }[];
    }
  | { tipo: "conjuntos-por-extension"; campos: string[]; correctas?: Record<string, number[]> }
  | { tipo: "emparejar"; consigna: string; izquierda: string[]; derecha: string[]; correctas?: string[] };

// --- Ejercicio y examen ---------------------------------------------------

export interface Paso {
  titulo: string;
  detalle: string;
}

export interface Ejercicio {
  tema: string;
  subtema: string;
  consigna: string;
  puntaje: number;
  visual: Visual;
  practica: Practica;
  pasos?: Paso[];
  respuesta?: string;
  observacion?: string;
  verificacion?: string;
}

export interface Examen {
  titulo: string;
  modo: string;
  semilla: number;
  puntaje_total: number;
  con_soluciones: boolean;
  ejercicios: Ejercicio[];
}

export interface Catalogo {
  modos: Record<string, { ejercicios: string[]; cantidad: number }>;
  temas: Record<string, string[]>;
  tipos: string[];
}

// --- Corrección -----------------------------------------------------------

export interface DetalleItem {
  esperado: unknown;
  dado: unknown;
  correcto: boolean;
  etiqueta: string;
}

export interface ResultadoEjercicio {
  ejercicio: number;
  subtema: string;
  puntaje: number;
  obtenidos: number;
  aciertos: number;
  total: number;
  detalle: DetalleItem[];
}

export interface Resultado {
  puntos: number;
  puntos_totales: number;
  aprobado: boolean;
  ejercicios: ResultadoEjercicio[];
}
