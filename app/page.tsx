"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { traerCatalogo } from "./lib/api";
import type { Catalogo } from "./lib/tipos";
import { clases } from "./lib/formato";

const DESCRIPCIONES: Record<string, string> = {
  integrador: "Las cuatro unidades, 100 puntos. Incluye el ejercicio que cruza Conjuntos con Relaciones.",
  parcial1: "Formato exacto del primer parcial: Lógica 40 %, Conjuntos 30 %, Relaciones 30 %.",
  completo: "Uno de cada tipo de ejercicio. Sirve para barrer todo antes del examen.",
  express: "Cuatro ejercicios cortos, para una repasada rápida.",
};

const TEMAS: Record<string, string> = {
  logica: "Lógica",
  conjuntos: "Conjuntos",
  relaciones: "Relaciones",
  funciones: "Funciones",
};

export default function Inicio() {
  const router = useRouter();
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [modo, setModo] = useState("integrador");
  const [tema, setTema] = useState<string | null>(null);
  const [semilla, setSemilla] = useState("");
  const [conSoluciones, setConSoluciones] = useState(true);

  useEffect(() => {
    traerCatalogo().then(setCatalogo).catch((e) => setError(String(e.message ?? e)));
  }, []);

  function generar() {
    const elegida = semilla.trim() ? Number(semilla.trim()) : Math.floor(Math.random() * 999_999) + 1;
    const params = new URLSearchParams();
    if (tema) params.set("tema", tema);
    else params.set("modo", modo);
    if (!conSoluciones) params.set("soluciones", "false");
    router.push(`/examen/${elegida}?${params.toString()}`);
  }

  return (
    <main className="mx-auto max-w-3xl px-5 py-16">
      <p className="chip mb-3" style={{ color: "var(--color-acento)" }}>
        Matemática I · TUPI · UNQ
      </p>
      <h1 className="text-4xl leading-tight tracking-tight">
        Generador de integradores
      </h1>
      <p className="mt-3 max-w-xl text-[1.05rem]" style={{ color: "var(--color-suave)" }}>
        Ejercicios al estilo de los prácticos y los parciales de la cátedra, con la
        resolución explicada paso a paso y los diagramas dibujados.
      </p>

      {error && (
        <div
          className="mt-8 rounded-lg border p-4 text-sm"
          style={{ borderColor: "var(--color-mal)", color: "var(--color-mal)" }}
        >
          No se pudo hablar con el generador: {error}
          <br />
          <span style={{ color: "var(--color-suave)" }}>
            ¿Está corriendo el backend? <code>npm run dev:api</code>
          </span>
        </div>
      )}

      <section className="mt-12">
        <h2 className="chip mb-3" style={{ color: "var(--color-suave)" }}>
          Qué querés practicar
        </h2>
        <div className="grid gap-2 sm:grid-cols-2">
          {Object.keys(catalogo?.modos ?? { integrador: null, parcial1: null }).map((nombre) => (
            <button
              key={nombre}
              onClick={() => {
                setModo(nombre);
                setTema(null);
              }}
              className={clases(
                "rounded-xl border p-4 text-left transition",
                !tema && modo === nombre ? "ring-2" : "",
              )}
              style={{
                borderColor: !tema && modo === nombre ? "var(--color-acento)" : "var(--color-borde)",
                background: !tema && modo === nombre ? "var(--color-acento-suave)" : "var(--color-superficie)",
                ...(!tema && modo === nombre ? { boxShadow: "0 0 0 1px var(--color-acento)" } : {}),
              }}
            >
              <div className="font-semibold capitalize">{nombre}</div>
              <div className="mt-1 text-[0.85rem]" style={{ color: "var(--color-suave)" }}>
                {DESCRIPCIONES[nombre] ?? ""}
              </div>
            </button>
          ))}
        </div>

        <h2 className="chip mt-8 mb-3" style={{ color: "var(--color-suave)" }}>
          O una sola unidad
        </h2>
        <div className="flex flex-wrap gap-2">
          {Object.entries(TEMAS).map(([clave, nombre]) => (
            <button
              key={clave}
              onClick={() => setTema(tema === clave ? null : clave)}
              className="rounded-full border px-4 py-1.5 text-sm transition"
              style={{
                borderColor: tema === clave ? "var(--color-acento)" : "var(--color-borde)",
                background: tema === clave ? "var(--color-acento-suave)" : "transparent",
              }}
            >
              {nombre}
            </button>
          ))}
        </div>
      </section>

      <section className="mt-10 flex flex-wrap items-end gap-4">
        <label className="block">
          <span className="chip block mb-1" style={{ color: "var(--color-suave)" }}>
            Semilla (opcional)
          </span>
          <input
            value={semilla}
            onChange={(e) => setSemilla(e.target.value.replace(/\D/g, ""))}
            placeholder="al azar"
            inputMode="numeric"
            className="w-36 rounded-lg border px-3 py-2 outline-none"
            style={{
              borderColor: "var(--color-borde)",
              background: "var(--color-superficie)",
              fontFamily: "var(--font-codigo)",
            }}
          />
        </label>

        <label className="flex cursor-pointer items-center gap-2 pb-2 text-sm">
          <input
            type="checkbox"
            checked={!conSoluciones}
            onChange={(e) => setConSoluciones(!e.target.checked)}
            className="size-4 accent-[var(--color-acento)]"
          />
          Modo examen (sin resolución)
        </label>

        <button
          onClick={generar}
          className="ml-auto rounded-lg px-6 py-2.5 font-medium text-white transition hover:opacity-90"
          style={{ background: "var(--color-acento)", fontFamily: "var(--font-interfaz)" }}
        >
          Generar
        </button>
      </section>

      <p className="mt-6 text-sm" style={{ color: "var(--color-suave)" }}>
        La semilla reproduce exactamente el mismo examen. Sirve para rendirlo en
        modo examen y después volver con la misma semilla para corregirte.
      </p>
    </main>
  );
}
