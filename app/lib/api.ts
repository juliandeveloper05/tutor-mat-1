import type { Catalogo, Examen, Resultado } from "./tipos";

/**
 * Cliente de la API. En desarrollo Next redirige /api/* al uvicorn local
 * (ver next.config.ts) y en producción Vercel lo manda a la función Python,
 * así que del lado del navegador la URL es siempre la misma.
 */

export interface OpcionesExamen {
  modo?: string;
  tema?: string | null;
  tipo?: string | null;
  cantidad?: number;
  semilla?: number | null;
  soluciones?: boolean;
}

async function pedir<T>(url: string, init?: RequestInit): Promise<T> {
  const respuesta = await fetch(url, init);
  if (!respuesta.ok) {
    const detalle = await respuesta.text();
    throw new Error(
      `La API respondió ${respuesta.status}. ${detalle.slice(0, 200)}`,
    );
  }
  return (await respuesta.json()) as T;
}

export function urlExamen(opciones: OpcionesExamen): string {
  const params = new URLSearchParams();
  if (opciones.modo) params.set("modo", opciones.modo);
  if (opciones.tema) params.set("tema", opciones.tema);
  if (opciones.tipo) params.set("tipo", opciones.tipo);
  if (opciones.cantidad) params.set("cantidad", String(opciones.cantidad));
  if (opciones.semilla != null) params.set("semilla", String(opciones.semilla));
  if (opciones.soluciones === false) params.set("soluciones", "false");
  return `/api/examen?${params.toString()}`;
}

export function traerExamen(opciones: OpcionesExamen): Promise<Examen> {
  return pedir<Examen>(urlExamen(opciones));
}

export function traerCatalogo(): Promise<Catalogo> {
  return pedir<Catalogo>("/api/tipos");
}

export function corregir(
  opciones: OpcionesExamen & { semilla: number },
  respuestas: unknown[],
): Promise<Resultado> {
  return pedir<Resultado>("/api/corregir", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      semilla: opciones.semilla,
      modo: opciones.modo ?? "integrador",
      tema: opciones.tema ?? null,
      tipo: opciones.tipo ?? null,
      cantidad: opciones.cantidad ?? 1,
      respuestas,
    }),
  });
}
