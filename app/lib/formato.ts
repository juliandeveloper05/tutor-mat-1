/** Utilidades chicas de presentación, compartidas por los componentes. */

import type { DominioJSON, Fraccion } from "./tipos";

/** Escribe una fracción como la escribiría una persona: −3/2, no −1.5. */
export function fraccion(f: Fraccion | null): string {
  if (f === null) return "∞";
  if (f.den === 1) return String(f.num).replace("-", "−");
  return `${String(f.num).replace("-", "−")}/${f.den}`;
}

export function dominioTexto(d: DominioJSON | undefined): string {
  return d?.texto ?? "";
}

/** Reparte una lista en columnas, para las grillas de opciones. */
export function agrupar<T>(lista: T[], tamanio: number): T[][] {
  const salida: T[][] = [];
  for (let i = 0; i < lista.length; i += tamanio) {
    salida.push(lista.slice(i, i + tamanio));
  }
  return salida;
}

/** Une clases condicionales sin traer una dependencia sólo para esto. */
export function clases(...partes: (string | false | null | undefined)[]): string {
  return partes.filter(Boolean).join(" ");
}
