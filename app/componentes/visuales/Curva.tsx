"use client";

import type { Muestra } from "../../lib/tipos";

/**
 * Gráfico de una o dos funciones.
 *
 * Los puntos vienen ya muestreados desde Python: acá no se evalúa ninguna
 * fórmula. Donde el backend manda `y = null` (fuera del dominio, o una
 * asíntota) se **levanta el trazo** en vez de unir ramas que no van unidas, que
 * es el error clásico al graficar una homográfica.
 */

const ANCHO = 420;
const ALTO = 300;

interface Serie {
  muestras: Muestra[];
  color: string;
  etiqueta: string;
  punteada?: boolean;
}

export function Curva({
  series,
  rango = 10,
  mostrarIdentidad = false,
}: {
  series: Serie[];
  rango?: number;
  mostrarIdentidad?: boolean;
}) {
  const margen = 8;
  const escala = (ANCHO - margen * 2) / (rango * 2);
  const cx = ANCHO / 2;
  const cy = ALTO / 2;
  const px = (x: number) => cx + x * escala;
  const py = (y: number) => cy - y * escala;

  const trazos = series.map((serie) => {
    const partes: string[] = [];
    let abierto = false;
    for (const [x, y] of serie.muestras) {
      if (y === null || Math.abs(y) > rango * 1.4) {
        abierto = false;
        continue;
      }
      partes.push(`${abierto ? "L" : "M"}${px(x).toFixed(1)},${py(y).toFixed(1)}`);
      abierto = true;
    }
    return { ...serie, d: partes.join(" ") };
  });

  const marcas = [];
  for (let v = -rango; v <= rango; v += Math.max(1, Math.round(rango / 5))) {
    if (v !== 0) marcas.push(v);
  }

  return (
    <div>
      <svg viewBox={`0 0 ${ANCHO} ${ALTO}`} style={{ width: "100%" }} role="img">
        <rect x="0" y="0" width={ANCHO} height={ALTO} rx="10" fill="var(--color-superficie)" stroke="var(--color-borde)" />
        {marcas.map((v) => (
          <g key={v} opacity="0.25">
            <line x1={px(v)} y1={margen} x2={px(v)} y2={ALTO - margen} stroke="var(--color-borde)" strokeWidth="1" />
            <line x1={margen} y1={py(v)} x2={ANCHO - margen} y2={py(v)} stroke="var(--color-borde)" strokeWidth="1" />
          </g>
        ))}
        <line x1={margen} y1={cy} x2={ANCHO - margen} y2={cy} stroke="var(--color-tinta)" strokeWidth="1.2" opacity="0.55" />
        <line x1={cx} y1={margen} x2={cx} y2={ALTO - margen} stroke="var(--color-tinta)" strokeWidth="1.2" opacity="0.55" />

        {mostrarIdentidad && (
          <line
            x1={px(-rango)}
            y1={py(-rango)}
            x2={px(rango)}
            y2={py(rango)}
            stroke="var(--color-suave)"
            strokeWidth="1"
            strokeDasharray="4 4"
            opacity="0.7"
          />
        )}

        {trazos.map((t, i) => (
          <path
            key={i}
            d={t.d}
            fill="none"
            stroke={t.color}
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeDasharray={t.punteada ? "6 4" : undefined}
          />
        ))}
      </svg>

      <div className="mt-2 flex flex-wrap gap-4 text-[0.82rem]" style={{ color: "var(--color-suave)" }}>
        {series.map((s, i) => (
          <span key={i} className="flex items-center gap-1.5">
            <span className="inline-block h-0.5 w-5" style={{ background: s.color }} />
            {s.etiqueta}
          </span>
        ))}
        {mostrarIdentidad && (
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-0.5 w-5" style={{ background: "var(--color-suave)" }} />
            y = x
          </span>
        )}
      </div>
    </div>
  );
}
