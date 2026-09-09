import type { NextConfig } from "next";

/**
 * El frontend siempre llama a /api/..., y de dónde sale ese /api cambia según
 * dónde corra:
 *
 *  - En Vercel lo resuelve vercel.json, que manda /api/* a la función Python.
 *  - Fuera de Vercel (tanto `next dev` como `next start` en tu máquina) Next se
 *    lo pasa al uvicorn local.
 *
 * La condición mira VERCEL y no NODE_ENV a propósito: con NODE_ENV se rompía al
 * probar el build de producción en local, porque el rewrite desaparecía y /api
 * quedaba en 404.
 */
const config: NextConfig = {
  async rewrites() {
    if (process.env.VERCEL) return [];
    const backend = process.env.API_URL ?? "http://127.0.0.1:8000";
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};

export default config;
