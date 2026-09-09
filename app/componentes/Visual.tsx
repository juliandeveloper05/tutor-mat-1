"use client";

import dynamic from "next/dynamic";
import type { Region } from "./visuales/Venn";
import { Cadena } from "./visuales/Cadena";
import { Curva } from "./visuales/Curva";
import { RectaReal } from "./visuales/RectaReal";
import { Venn } from "./visuales/Venn";
import { Mate } from "./Mate";
import type { Visual as TipoVisual } from "../lib/tipos";

// Three.js sólo se carga cuando hace falta un diagrama de Hasse: no tiene
// sentido que pese en los ejercicios de lógica o de funciones.
const Hasse3D = dynamic(() => import("./visuales/Hasse3D").then((m) => m.Hasse3D), {
  ssr: false,
  loading: () => (
    <div
      className="grid h-[340px] place-items-center rounded-xl border text-sm"
      style={{ borderColor: "var(--color-borde)", color: "var(--color-suave)" }}
    >
      Dibujando el diagrama…
    </div>
  ),
});

const NOMBRE_REGION: Record<string, Region> = {
  a: "a", b: "b", c: "c", ab: "ab", ac: "ac", bc: "bc", abc: "abc", afuera: "afuera",
};

/**
 * Elige qué dibujar según el tipo de ejercicio y sincroniza el resaltado con el
 * paso de la resolución que el usuario está mirando.
 */
export function Visual({
  visual,
  paso,
  totalPasos,
}: {
  visual: TipoVisual;
  paso: number;
  totalPasos: number;
}) {
  switch (visual.tipo) {
    case "cadena-logica": {
      if (!visual.pasos?.length) {
        return (
          <Recuadro titulo="Fórmula a simplificar">
            <Mate latex={visual.inicial.latex} texto={visual.inicial.texto} display />
          </Recuadro>
        );
      }
      // Los dos primeros pasos del texto son la explicación del método.
      const desfase = Math.max(0, totalPasos - 1 - visual.pasos.length);
      return (
        <Cadena
          inicial={visual.inicial}
          pasos={visual.pasos}
          activo={Math.min(visual.pasos.length - 1, Math.max(0, paso - desfase))}
        />
      );
    }

    case "cadena-conjuntos": {
      const variables = visual.variables;
      return (
        <div className="space-y-4">
          {visual.pasos?.length ? (
            <Cadena
              inicial={visual.inicial}
              pasos={visual.pasos}
              activo={Math.min(visual.pasos.length - 1, Math.max(0, paso - 1))}
              simbolo="="
            />
          ) : (
            <Recuadro titulo="Hay que demostrar">
              <Mate latex={`${visual.inicial.latex} = ${visual.final.latex}`} display />
            </Recuadro>
          )}
          {visual.celdas_inicial && visual.celdas_final && (
            <div>
              <p className="chip mb-2" style={{ color: "var(--color-suave)" }}>
                Ambos miembros pintan las mismas regiones
              </p>
              <div className="grid grid-cols-2 gap-2">
                <VennCeldas variables={variables} celdas={visual.celdas_inicial} pie={visual.inicial.texto} />
                <VennCeldas variables={variables} celdas={visual.celdas_final} pie={visual.final.texto} />
              </div>
            </div>
          )}
        </div>
      );
    }

    case "venn-conteo": {
      // El diagrama arranca **vacío**: llenar las regiones es justamente el
      // ejercicio. Los números aparecen recién en el paso donde se deducen,
      // igual que se haría en papel.
      const yaSeDedujo = paso >= 1;
      const desfase = totalPasos - (visual.resaltados?.length ?? 0);
      const indicePregunta = paso - desfase;
      const resaltadas =
        indicePregunta >= 0 && visual.resaltados?.[indicePregunta]
          ? visual.resaltados[indicePregunta].regiones.map((r) => NOMBRE_REGION[r])
          : [];
      return (
        <Recuadro titulo={`Total: ${visual.total} ${visual.unidad}`}>
          <Venn
            letras={visual.letras as [string, string, string]}
            contenido={yaSeDedujo ? (visual.regiones ?? {}) : {}}
            resaltadas={resaltadas}
          />
          {!yaSeDedujo && (
            <p className="text-center text-[0.8rem]" style={{ color: "var(--color-suave)" }}>
              Las regiones se completan en el paso 2 de la resolución.
            </p>
          )}
        </Recuadro>
      );
    }

    case "venn-elementos": {
      const contenido: Partial<Record<Region, string>> = {};
      for (const [clave, valores] of Object.entries(visual.regiones ?? {})) {
        contenido[NOMBRE_REGION[clave]] = valores.join(" ");
      }
      return (
        <Recuadro titulo="Ubicación de los elementos">
          <Venn letras={visual.letras as [string, string, string]} contenido={contenido} />
        </Recuadro>
      );
    }

    case "hasse": {
      const p = visual.particulares;
      const resaltados = new Set<string>(p?.subconjunto ?? []);
      // En el último paso se habla de cotas: se agregan al resaltado.
      if (p && paso >= totalPasos - 1) {
        for (const e of [...p.cotas_superiores, ...p.cotas_inferiores]) resaltados.add(e);
      }
      // La tabla de elementos particulares es la respuesta del ejercicio: se
      // muestra recién en el paso que la explica, no al lado del formulario.
      const revelarTabla = paso >= totalPasos - 1;
      return (
        <div>
          <Hasse3D visual={visual} resaltados={[...resaltados]} />
          {p && revelarTabla && <TablaParticulares visual={visual} />}
        </div>
      );
    }

    case "cuantificadores":
      return (
        <Recuadro titulo="Conjuntos de verdad sobre ℤ">
          <div className="space-y-3">
            {visual.predicados.map((pred) => (
              <RectaReal
                key={pred.nombre}
                puntos={pred.puntos}
                desde={-12}
                hasta={12}
                etiqueta={`${pred.nombre}(x): ${pred.texto}${
                  pred.conjunto_verdad ? ` — V(${pred.nombre}) = ${pred.conjunto_verdad}` : ""
                }`}
              />
            ))}
          </div>
        </Recuadro>
      );

    case "dominio":
      return (
        <Recuadro titulo={visual.funcion}>
          {visual.dominio && <RectaReal dominio={visual.dominio} etiqueta={`Dom f = ${visual.dominio.texto}`} />}
          {visual.muestras && (
            <div className="mt-3">
              <Curva series={[{ muestras: visual.muestras, color: "var(--color-acento)", etiqueta: "f(x)" }]} />
            </div>
          )}
        </Recuadro>
      );

    case "funcion-inversa":
      return (
        <Recuadro titulo={visual.funcion}>
          {visual.muestras_f && (
            <Curva
              mostrarIdentidad
              series={[
                { muestras: visual.muestras_f, color: "var(--color-acento)", etiqueta: "f" },
                ...(visual.muestras_inversa
                  ? [
                      {
                        muestras: visual.muestras_inversa,
                        color: "var(--color-bien)",
                        etiqueta: "f⁻¹",
                        punteada: true,
                      },
                    ]
                  : []),
              ]}
            />
          )}
          {visual.dominio && (
            <p className="mt-2 text-[0.85rem]" style={{ color: "var(--color-suave)" }}>
              f y f⁻¹ son simétricas respecto de la recta y = x.
            </p>
          )}
        </Recuadro>
      );

    case "composicion":
      return (
        <div className="space-y-3">
          {visual.gf && (
            <Recuadro titulo={visual.gf.texto}>
              <RectaReal dominio={visual.gf.dominio} etiqueta={`Dom = ${visual.gf.dominio.texto}`} />
            </Recuadro>
          )}
          {visual.fg && (
            <Recuadro titulo={visual.fg.texto}>
              <RectaReal dominio={visual.fg.dominio} etiqueta={`Dom = ${visual.fg.dominio.texto}`} />
            </Recuadro>
          )}
          {!visual.gf && !visual.fg && (
            <Recuadro titulo="Composición">
              <p style={{ color: "var(--color-suave)" }}>
                {visual.f} · {visual.g}
              </p>
            </Recuadro>
          )}
        </div>
      );

    case "relacion":
    case "equivalencia":
      return (
        <Recuadro titulo={`R sobre A = {${visual.A.join(", ")}}`}>
          <MatrizRelacion A={visual.A} pares={visual.pares} />
        </Recuadro>
      );

    case "derivacion":
      return (
        <Recuadro titulo="Premisas y conclusión">
          <div className="space-y-1.5">
            {visual.premisas.map((p, i) => (
              <div key={i} className="flex gap-3">
                <span className="chip w-4" style={{ color: "var(--color-suave)" }}>
                  {i + 1}
                </span>
                <Mate latex={p.latex} texto={p.texto} />
              </div>
            ))}
            <div className="flex gap-3 border-t pt-2" style={{ borderColor: "var(--color-borde)" }}>
              <span className="w-4" style={{ color: "var(--color-suave)" }}>
                ∴
              </span>
              <Mate latex={visual.meta.latex} texto={visual.meta.texto} />
            </div>
          </div>
        </Recuadro>
      );

    default:
      return null;
  }
}

function Recuadro({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="chip mb-2" style={{ color: "var(--color-suave)" }}>
        {titulo}
      </p>
      {children}
    </div>
  );
}

/** Un Venn chico que pinta las celdas del álgebra de Boole libre. */
function VennCeldas({
  variables,
  celdas,
  pie,
}: {
  variables: string[];
  celdas: boolean[][];
  pie: string;
}) {
  // Cada celda es un vector de pertenencia; se traduce al nombre de región.
  const activas = new Set<Region>();
  for (const celda of celdas) {
    const [enA, enB, enC] = [celda[0] ?? false, celda[1] ?? false, celda[2] ?? false];
    const clave = `${enA ? "a" : ""}${enB ? "b" : ""}${enC ? "c" : ""}` || "afuera";
    if (clave in NOMBRE_REGION) activas.add(NOMBRE_REGION[clave]);
  }
  return (
    <div>
      <Venn
        letras={[variables[0] ?? "A", variables[1] ?? "B", variables[2] ?? "C"]}
        resaltadas={[...activas]}
        alto={190}
      />
      <p className="mt-1 text-center text-[0.78rem]" style={{ color: "var(--color-suave)" }}>
        {pie}
      </p>
    </div>
  );
}

function MatrizRelacion({ A, pares }: { A: string[]; pares: [string, string][] }) {
  const conjunto = new Set(pares.map(([x, y]) => `${x}|${y}`));
  return (
    <table className="text-center text-sm" style={{ fontFamily: "var(--font-codigo)" }}>
      <thead>
        <tr>
          <th className="p-1.5" />
          {A.map((y) => (
            <th key={y} className="p-1.5" style={{ color: "var(--color-suave)" }}>
              {y}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {A.map((x) => (
          <tr key={x}>
            <th className="p-1.5" style={{ color: "var(--color-suave)" }}>
              {x}
            </th>
            {A.map((y) => {
              const hay = conjunto.has(`${x}|${y}`);
              return (
                <td key={y} className="p-1.5">
                  <span
                    className="inline-grid size-6 place-items-center rounded"
                    style={{
                      background: hay ? "var(--color-acento)" : "var(--color-borde)",
                      color: hay ? "#fff" : "transparent",
                      opacity: hay ? 1 : 0.35,
                    }}
                  >
                    ●
                  </span>
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function TablaParticulares({ visual }: { visual: Extract<TipoVisual, { tipo: "hasse" }> }) {
  const p = visual.particulares;
  if (!p) return null;
  const nombre = (e: string | null) => (e ? (visual.etiquetas[e] ?? e) : "no tiene");
  const lista = (xs: string[]) =>
    xs.length ? xs.map((e) => visual.etiquetas[e] ?? e).join(", ") : "∅";

  const filas: [string, string][] = [
    ["Maximales", lista(p.maximales)],
    ["Minimales", lista(p.minimales)],
    ["Máximo", nombre(p.maximo)],
    ["Mínimo", nombre(p.minimo)],
    ["Cotas superiores", lista(p.cotas_superiores)],
    ["Cotas inferiores", lista(p.cotas_inferiores)],
    ["Supremo", nombre(p.supremo)],
    ["Ínfimo", nombre(p.infimo)],
  ];

  return (
    <table className="mt-4 w-full text-[0.86rem]">
      <tbody>
        {filas.map(([etiqueta, valor]) => (
          <tr key={etiqueta} className="border-b" style={{ borderColor: "var(--color-borde)" }}>
            <td className="chip py-1.5 pr-3" style={{ color: "var(--color-suave)" }}>
              {etiqueta}
            </td>
            <td className="py-1.5" style={{ fontFamily: "var(--font-codigo)" }}>
              {valor}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
