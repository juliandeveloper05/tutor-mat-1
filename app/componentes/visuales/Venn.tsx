"use client";

import { useId } from "react";
import { clases } from "../../lib/formato";

/**
 * Diagrama de Venn de tres conjuntos con las ocho regiones dibujadas de forma
 * exacta.
 *
 * La intersección se logra anidando `clipPath` (cada uno recorta al anterior) y
 * la resta con una `mask` que pinta de negro lo que hay que sacar. Así "sólo A"
 * es de verdad A − (B ∪ C) y no una aproximación dibujada a ojo: al resaltar
 * una región se ilumina exactamente el área que corresponde.
 */

const R = 58;
const CENTROS = {
  A: { cx: 104, cy: 100 },
  B: { cx: 152, cy: 100 },
  C: { cx: 128, cy: 142 },
};

/** Dónde cae el número de cada región. */
const ETIQUETAS: Record<string, { x: number; y: number }> = {
  a: { x: 76, y: 90 },
  b: { x: 180, y: 90 },
  c: { x: 128, y: 172 },
  ab: { x: 128, y: 76 },
  ac: { x: 98, y: 130 },
  bc: { x: 158, y: 130 },
  abc: { x: 128, y: 114 },
  afuera: { x: 232, y: 206 },
};

export type Region = "a" | "b" | "c" | "ab" | "ac" | "bc" | "abc" | "afuera";

export interface PropsVenn {
  letras?: [string, string, string];
  /** Número o lista de elementos que va en cada región. */
  contenido?: Partial<Record<Region, string | number>>;
  /** Regiones a resaltar con el color de acento. */
  resaltadas?: Region[];
  onRegion?: (region: Region) => void;
  alto?: number;
}

export function Venn({
  letras = ["A", "B", "C"],
  contenido = {},
  resaltadas = [],
  onRegion,
  alto = 300,
}: PropsVenn) {
  const id = useId().replace(/:/g, "");
  const clip = (k: string) => `clip-${id}-${k}`;
  const mask = (k: string) => `mask-${id}-${k}`;
  const activa = (r: Region) => resaltadas.includes(r);

  // Cada región: qué círculos la recortan y cuáles se le restan.
  const REGIONES: { clave: Region; recorta: ("A" | "B" | "C")[]; resta: ("A" | "B" | "C")[] }[] = [
    { clave: "a", recorta: ["A"], resta: ["B", "C"] },
    { clave: "b", recorta: ["B"], resta: ["A", "C"] },
    { clave: "c", recorta: ["C"], resta: ["A", "B"] },
    { clave: "ab", recorta: ["A", "B"], resta: ["C"] },
    { clave: "ac", recorta: ["A", "C"], resta: ["B"] },
    { clave: "bc", recorta: ["B", "C"], resta: ["A"] },
    { clave: "abc", recorta: ["A", "B", "C"], resta: [] },
  ];

  return (
    <svg
      viewBox="0 0 256 224"
      style={{ height: alto, width: "100%" }}
      role="img"
      aria-label="Diagrama de Venn de tres conjuntos"
    >
      <defs>
        {(["A", "B", "C"] as const).map((k) => (
          <clipPath key={k} id={clip(k)}>
            <circle cx={CENTROS[k].cx} cy={CENTROS[k].cy} r={R} />
          </clipPath>
        ))}
        {REGIONES.filter((r) => r.resta.length > 0).map((r) => (
          <mask key={r.clave} id={mask(r.clave)}>
            <rect x="0" y="0" width="256" height="224" fill="white" />
            {r.resta.map((k) => (
              <circle key={k} cx={CENTROS[k].cx} cy={CENTROS[k].cy} r={R} fill="black" />
            ))}
          </mask>
        ))}
        <mask id={mask("afuera")}>
          <rect x="0" y="0" width="256" height="224" fill="white" />
          {(["A", "B", "C"] as const).map((k) => (
            <circle key={k} cx={CENTROS[k].cx} cy={CENTROS[k].cy} r={R} fill="black" />
          ))}
        </mask>
      </defs>

      {/* Región exterior */}
      <rect
        x="1"
        y="1"
        width="254"
        height="222"
        rx="10"
        mask={`url(#${mask("afuera")})`}
        fill={activa("afuera") ? "var(--color-acento-suave)" : "transparent"}
        className={clases(onRegion && "cursor-pointer")}
        onClick={() => onRegion?.("afuera")}
      />

      {/* Las siete regiones interiores, cada una recortada e intersecada */}
      {REGIONES.map(({ clave, recorta, resta }) => {
        const relleno = activa(clave) ? "var(--color-acento)" : "var(--color-acento)";
        const opacidad = activa(clave) ? 0.28 : 0.07;
        let nodo = (
          <rect
            x="0"
            y="0"
            width="256"
            height="224"
            fill={relleno}
            opacity={opacidad}
            mask={resta.length ? `url(#${mask(clave)})` : undefined}
            className={clases(onRegion && "cursor-pointer")}
            onClick={() => onRegion?.(clave)}
          />
        );
        // Se anidan los clip: cada uno recorta lo que quedó del anterior.
        for (const k of recorta) {
          nodo = <g clipPath={`url(#${clip(k)})`}>{nodo}</g>;
        }
        return <g key={clave}>{nodo}</g>;
      })}

      {/* Contornos */}
      {(["A", "B", "C"] as const).map((k) => (
        <circle
          key={k}
          cx={CENTROS[k].cx}
          cy={CENTROS[k].cy}
          r={R}
          fill="none"
          stroke="var(--color-tinta)"
          strokeWidth="1.1"
          opacity="0.5"
        />
      ))}

      {/* Nombres de los conjuntos */}
      <text x="58" y="52" textAnchor="middle" fontSize="15" fill="var(--color-tinta)" fontWeight="600">
        {letras[0]}
      </text>
      <text x="198" y="52" textAnchor="middle" fontSize="15" fill="var(--color-tinta)" fontWeight="600">
        {letras[1]}
      </text>
      <text x="128" y="214" textAnchor="middle" fontSize="15" fill="var(--color-tinta)" fontWeight="600">
        {letras[2]}
      </text>

      {/* Contenido de cada región */}
      {(Object.keys(ETIQUETAS) as Region[]).map((region) => {
        const valor = contenido[region];
        if (valor === undefined || valor === "") return null;
        const { x, y } = ETIQUETAS[region];
        return (
          <text
            key={region}
            x={x}
            y={y}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize={String(valor).length > 6 ? 9 : 12}
            fontWeight={activa(region) ? 700 : 500}
            fill={activa(region) ? "var(--color-acento)" : "var(--color-tinta)"}
            style={{ fontFamily: "var(--font-codigo)", pointerEvents: "none" }}
          >
            {valor}
          </text>
        );
      })}
    </svg>
  );
}
