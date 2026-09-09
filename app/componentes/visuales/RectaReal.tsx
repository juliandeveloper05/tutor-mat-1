"use client";

import { fraccion } from "../../lib/formato";
import type { DominioJSON } from "../../lib/tipos";

/**
 * Recta real con intervalos.
 *
 * Dibuja la diferencia que más se corrige en el parcial: el extremo cerrado va
 * con punto lleno y el abierto con punto hueco. Los puntos excluidos (los que
 * anulan un denominador) se marcan con una cruz.
 *
 * Sirve también para los conjuntos de verdad de los cuantificadores, pasando
 * `puntos` en vez de un dominio.
 */

const ANCHO = 520;
const ALTO = 92;
const EJE = 54;

export function RectaReal({
  dominio,
  puntos,
  desde = -10,
  hasta = 10,
  etiqueta,
}: {
  dominio?: DominioJSON;
  puntos?: number[];
  desde?: number;
  hasta?: number;
  etiqueta?: string;
}) {
  const margen = 26;
  const util = ANCHO - margen * 2;
  const x = (valor: number) =>
    margen + ((Math.max(desde, Math.min(hasta, valor)) - desde) / (hasta - desde)) * util;

  const marcas: number[] = [];
  const paso = Math.max(1, Math.round((hasta - desde) / 10));
  for (let v = Math.ceil(desde); v <= hasta; v += paso) marcas.push(v);

  return (
    <div>
      {etiqueta && (
        <p className="chip mb-1" style={{ color: "var(--color-suave)" }}>
          {etiqueta}
        </p>
      )}
      <svg viewBox={`0 0 ${ANCHO} ${ALTO}`} style={{ width: "100%" }} role="img">
        {/* Eje */}
        <line
          x1={margen - 14}
          y1={EJE}
          x2={ANCHO - margen + 14}
          y2={EJE}
          stroke="var(--color-tinta)"
          strokeWidth="1.2"
          opacity="0.6"
        />
        <polygon
          points={`${ANCHO - margen + 14},${EJE} ${ANCHO - margen + 6},${EJE - 4} ${ANCHO - margen + 6},${EJE + 4}`}
          fill="var(--color-tinta)"
          opacity="0.6"
        />

        {marcas.map((v) => (
          <g key={v}>
            <line x1={x(v)} y1={EJE - 4} x2={x(v)} y2={EJE + 4} stroke="var(--color-tinta)" strokeWidth="1" opacity="0.35" />
            <text
              x={x(v)}
              y={EJE + 20}
              textAnchor="middle"
              fontSize="10"
              fill="var(--color-suave)"
              style={{ fontFamily: "var(--font-codigo)" }}
            >
              {String(v).replace("-", "−")}
            </text>
          </g>
        ))}

        {/* Intervalos del dominio */}
        {dominio?.intervalos.map((intervalo, i) => {
          const x1 = intervalo.izq === null ? margen - 12 : x(intervalo.izq.valor);
          const x2 = intervalo.der === null ? ANCHO - margen + 12 : x(intervalo.der.valor);
          return (
            <g key={i}>
              <line x1={x1} y1={EJE} x2={x2} y2={EJE} stroke="var(--color-acento)" strokeWidth="4" strokeLinecap="round" />
              {intervalo.izq !== null && (
                <>
                  <circle
                    cx={x1}
                    cy={EJE}
                    r="5.5"
                    fill={intervalo.izq_cerrado ? "var(--color-acento)" : "var(--color-superficie)"}
                    stroke="var(--color-acento)"
                    strokeWidth="2"
                  />
                  <text x={x1} y={EJE - 14} textAnchor="middle" fontSize="11" fill="var(--color-acento)" style={{ fontFamily: "var(--font-codigo)" }}>
                    {fraccion(intervalo.izq)}
                  </text>
                </>
              )}
              {intervalo.der !== null && (
                <>
                  <circle
                    cx={x2}
                    cy={EJE}
                    r="5.5"
                    fill={intervalo.der_cerrado ? "var(--color-acento)" : "var(--color-superficie)"}
                    stroke="var(--color-acento)"
                    strokeWidth="2"
                  />
                  <text x={x2} y={EJE - 14} textAnchor="middle" fontSize="11" fill="var(--color-acento)" style={{ fontFamily: "var(--font-codigo)" }}>
                    {fraccion(intervalo.der)}
                  </text>
                </>
              )}
            </g>
          );
        })}

        {/* Puntos excluidos */}
        {dominio?.excluidos.map((e, i) => (
          <g key={`x-${i}`}>
            <circle cx={x(e.valor)} cy={EJE} r="5.5" fill="var(--color-papel)" stroke="var(--color-mal)" strokeWidth="2" />
            <text x={x(e.valor)} y={EJE - 14} textAnchor="middle" fontSize="11" fill="var(--color-mal)" style={{ fontFamily: "var(--font-codigo)" }}>
              {fraccion(e)}
            </text>
          </g>
        ))}

        {/* Puntos sueltos (conjuntos de verdad de predicados enteros) */}
        {puntos?.map((p) => (
          <circle key={p} cx={x(p)} cy={EJE} r="4.5" fill="var(--color-acento)" />
        ))}
      </svg>
    </div>
  );
}
