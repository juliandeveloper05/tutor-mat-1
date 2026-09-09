"use client";

import { Fragment, type ReactNode } from "react";

/**
 * Renderiza el Markdown acotado que produce `mategen`: negritas, código,
 * bloques, listas, tablas y párrafos. No es un motor general —no hace falta—
 * pero cubre exactamente lo que el backend emite.
 *
 * Los bloques ```mermaid se descartan a propósito: el diagrama ahora lo dibuja
 * el componente visual, mucho mejor que ese texto.
 */

function enLinea(texto: string, clave: string): ReactNode {
  // Se parte por `código` y **negrita**, en ese orden.
  const partes = texto.split(/(`[^`]*`|\*\*[^*]+\*\*)/g);
  return partes.map((parte, i) => {
    const k = `${clave}-${i}`;
    if (parte.startsWith("`") && parte.endsWith("`") && parte.length > 1) {
      return (
        <code
          key={k}
          className="rounded px-1 py-0.5 text-[0.88em]"
          style={{ background: "var(--color-acento-suave)", fontFamily: "var(--font-codigo)" }}
        >
          {parte.slice(1, -1)}
        </code>
      );
    }
    if (parte.startsWith("**") && parte.endsWith("**") && parte.length > 4) {
      return (
        <strong key={k} className="font-semibold">
          {parte.slice(2, -2)}
        </strong>
      );
    }
    return <Fragment key={k}>{parte}</Fragment>;
  });
}

export function Markdown({ texto }: { texto: string }) {
  const lineas = texto.split("\n");
  const bloques: ReactNode[] = [];
  let i = 0;

  while (i < lineas.length) {
    const linea = lineas[i];

    // Bloque de código
    if (linea.trimStart().startsWith("```")) {
      const lenguaje = linea.trim().slice(3).trim();
      i += 1;
      const cuerpo: string[] = [];
      while (i < lineas.length && !lineas[i].trimStart().startsWith("```")) {
        cuerpo.push(lineas[i]);
        i += 1;
      }
      i += 1;
      if (lenguaje !== "mermaid") {
        bloques.push(
          <pre
            key={`pre-${i}`}
            className="my-3 overflow-x-auto rounded-lg border p-3 text-[0.82rem] leading-relaxed"
            style={{
              background: "var(--color-superficie)",
              borderColor: "var(--color-borde)",
              fontFamily: "var(--font-codigo)",
            }}
          >
            {cuerpo.join("\n")}
          </pre>,
        );
      }
      continue;
    }

    // Tabla
    const siguiente = lineas[i + 1] ?? "";
    const esSeparador = /^\|[\s:|-]+\|?$/.test(siguiente.trim());
    if (linea.trim().startsWith("|") && esSeparador) {
      const celdas = (fila: string) =>
        fila.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      const encabezado = celdas(linea);
      i += 2;
      const filas: string[][] = [];
      while (i < lineas.length && lineas[i].trim().startsWith("|")) {
        filas.push(celdas(lineas[i]));
        i += 1;
      }
      bloques.push(
        <div key={`tabla-${i}`} className="my-3 overflow-x-auto">
          <table className="w-full border-collapse text-[0.9rem]">
            <thead>
              <tr>
                {encabezado.map((c, j) => (
                  <th
                    key={j}
                    className="chip border px-2 py-1 text-left"
                    style={{ borderColor: "var(--color-borde)", background: "var(--color-superficie)" }}
                  >
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filas.map((fila, j) => (
                <tr key={j}>
                  {fila.map((c, k) => (
                    <td key={k} className="border px-2 py-1" style={{ borderColor: "var(--color-borde)" }}>
                      {enLinea(c, `t-${j}-${k}`)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
      continue;
    }

    // Listas
    if (/^\s*[-*]\s+/.test(linea)) {
      const items: string[] = [];
      while (i < lineas.length && /^\s*[-*]\s+/.test(lineas[i])) {
        items.push(lineas[i].replace(/^\s*[-*]\s+/, ""));
        i += 1;
      }
      bloques.push(
        <ul key={`ul-${i}`} className="my-2 list-disc space-y-1 pl-5">
          {items.map((t, j) => (
            <li key={j}>{enLinea(t, `li-${j}`)}</li>
          ))}
        </ul>,
      );
      continue;
    }
    if (/^\s*\d+[.)]\s+/.test(linea)) {
      const items: string[] = [];
      while (i < lineas.length && /^\s*\d+[.)]\s+/.test(lineas[i])) {
        items.push(lineas[i].replace(/^\s*\d+[.)]\s+/, ""));
        i += 1;
      }
      bloques.push(
        <ol key={`ol-${i}`} className="my-2 list-decimal space-y-1 pl-5">
          {items.map((t, j) => (
            <li key={j}>{enLinea(t, `oli-${j}`)}</li>
          ))}
        </ol>,
      );
      continue;
    }

    // Párrafo
    if (linea.trim()) {
      const cuerpo: string[] = [];
      while (
        i < lineas.length &&
        lineas[i].trim() &&
        !lineas[i].trimStart().startsWith("```") &&
        !/^\s*[-*]\s+/.test(lineas[i]) &&
        !/^\s*\d+[.)]\s+/.test(lineas[i]) &&
        !lineas[i].trim().startsWith("|")
      ) {
        cuerpo.push(lineas[i]);
        i += 1;
      }
      bloques.push(
        <p key={`p-${i}`} className="my-2">
          {cuerpo.map((l, j) => (
            <Fragment key={j}>
              {j > 0 && <br />}
              {enLinea(l, `p-${i}-${j}`)}
            </Fragment>
          ))}
        </p>,
      );
      continue;
    }
    i += 1;
  }

  return <div className="mate">{bloques}</div>;
}
