"use client";

import { useEffect, useState } from "react";
import { Mate } from "../Mate";
import { clases } from "../../lib/formato";

/**
 * La cadena de equivalencias (o de igualdades de conjuntos), con el paso activo
 * resaltado y el detalle de qué se reescribió.
 *
 * Sincronizar esto con el stepper del texto es lo que la salida en Markdown no
 * podía hacer: al avanzar un paso se ve exactamente qué cambió y por qué ley.
 */

export interface RenglonCadena {
  ley: string;
  completa: { texto: string; latex: string };
  antes?: { texto: string; latex: string } | null;
  despues?: { texto: string; latex: string } | null;
}

export function Cadena({
  inicial,
  pasos,
  activo,
  simbolo = "≡",
  onElegir,
}: {
  inicial: { texto: string; latex: string };
  pasos: RenglonCadena[];
  activo: number;
  simbolo?: string;
  onElegir?: (indice: number) => void;
}) {
  // La cadena tiene su propio cursor porque casi nunca hay tantos pasos en el
  // texto como renglones en la cadena: sin esto no habría forma de llegar a
  // ver los últimos renglones.
  const [cursor, setCursor] = useState(activo);
  useEffect(() => setCursor(activo), [activo]);
  const visible = Math.min(pasos.length - 1, Math.max(cursor, activo));
  const detalle = visible >= 0 && visible < pasos.length ? pasos[visible] : null;

  return (
    <div>
      <div
        className="overflow-x-auto rounded-xl border p-4"
        style={{ background: "var(--color-superficie)", borderColor: "var(--color-borde)" }}
      >
        <div className="flex items-start gap-3 py-1">
          <span className="w-5 shrink-0" />
          <Mate latex={inicial.latex} texto={inicial.texto} className="text-[1.05rem]" />
        </div>

        {pasos.map((paso, i) => {
          const esActivo = i === visible;
          const yaVisto = i <= visible;
          // Los pasos que todavía no se abrieron no se muestran: en este
          // ejercicio la fórmula siguiente y el nombre de la ley **son** la
          // respuesta, así que mostrarlos de entrada convierte el stepper en
          // adorno y el panel de práctica en un copiar y pegar.
          return (
            <button
              key={i}
              onClick={() => {
                setCursor(i);
                onElegir?.(i);
              }}
              className={clases(
                // En pantalla angosta la fórmula y el nombre de la ley no
                // entran uno al lado del otro: se apilan. Si compiten por el
                // ancho, la fórmula queda exprimida en una columna de dos
                // caracteres y la ley se corta.
                "flex w-full cursor-pointer flex-col gap-0.5 rounded-lg py-1.5",
                "text-left transition sm:flex-row sm:items-start sm:gap-3",
              )}
              style={{
                background: esActivo ? "var(--color-acento-suave)" : "transparent",
                paddingInline: esActivo ? "0.5rem" : 0,
              }}
            >
              <span className="flex min-w-0 flex-1 items-start gap-3">
                <span
                  className="w-5 shrink-0 text-center"
                  style={{ color: "var(--color-suave)", fontFamily: "var(--font-codigo)" }}
                >
                  {yaVisto ? simbolo : ""}
                </span>
                <span className="min-w-0 flex-1">
                  {yaVisto ? (
                    <Mate
                      latex={paso.completa.latex}
                      texto={paso.completa.texto}
                      className="text-[1.05rem]"
                    />
                  ) : (
                    <span
                      className="inline-block h-4 w-full max-w-[14rem] rounded"
                      style={{ background: "var(--color-borde)", opacity: 0.5 }}
                    />
                  )}
                </span>
              </span>
              <span
                className="chip shrink-0 pl-8 sm:pl-0 sm:pt-1"
                style={{ color: esActivo ? "var(--color-acento)" : "var(--color-suave)" }}
              >
                {yaVisto ? `(${i + 1}) ${paso.ley}` : `(${i + 1})`}
              </span>
            </button>
          );
        })}
      </div>

      <div className="mt-2 flex items-center gap-2">
        <button
          onClick={() => setCursor((c) => Math.max(0, Math.min(c, visible) - 1))}
          disabled={visible <= 0}
          className="rounded border px-2 py-0.5 text-sm disabled:opacity-30"
          style={{ borderColor: "var(--color-borde)" }}
          aria-label="Paso anterior de la cadena"
        >
          ◀
        </button>
        <button
          onClick={() => setCursor((c) => Math.min(pasos.length - 1, Math.max(c, visible) + 1))}
          disabled={visible >= pasos.length - 1}
          className="rounded border px-2 py-0.5 text-sm disabled:opacity-30"
          style={{ borderColor: "var(--color-borde)" }}
          aria-label="Paso siguiente de la cadena"
        >
          ▶
        </button>
        <span className="chip" style={{ color: "var(--color-suave)" }}>
          paso {visible + 1} de {pasos.length}
        </span>
        <button
          onClick={() => setCursor(pasos.length - 1)}
          className="chip ml-auto underline"
          style={{ color: "var(--color-acento)" }}
        >
          ver toda la cadena
        </button>
      </div>

      {detalle?.antes && detalle?.despues && (
        <div
          className="mt-3 rounded-lg border p-3 text-[0.92rem]"
          style={{ borderColor: "var(--color-acento)", background: "var(--color-acento-suave)" }}
        >
          <span className="chip mr-2" style={{ color: "var(--color-acento)" }}>
            Paso {visible + 1}
          </span>
          Se reemplazó <Mate latex={detalle.antes.latex} texto={detalle.antes.texto} /> por{" "}
          <Mate latex={detalle.despues.latex} texto={detalle.despues.texto} />.
        </div>
      )}
    </div>
  );
}
