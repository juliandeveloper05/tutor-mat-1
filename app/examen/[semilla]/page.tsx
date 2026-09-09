"use client";

import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useMemo, useState } from "react";
import { Markdown } from "../../componentes/Markdown";
import { Practica } from "../../componentes/Practica";
import { Visual } from "../../componentes/Visual";
import { corregir as pedirCorreccion, traerExamen } from "../../lib/api";
import { clases } from "../../lib/formato";
import type { Examen, Resultado } from "../../lib/tipos";

function Contenido() {
  const params = useParams<{ semilla: string }>();
  const search = useSearchParams();
  const semilla = Number(params.semilla);

  const opciones = useMemo(
    () => ({
      modo: search.get("modo") ?? undefined,
      tema: search.get("tema"),
      tipo: search.get("tipo"),
      semilla,
      soluciones: search.get("soluciones") !== "false",
    }),
    [search, semilla],
  );

  const [examen, setExamen] = useState<Examen | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [indice, setIndice] = useState(0);
  const [paso, setPaso] = useState(0);
  const [respuestas, setRespuestas] = useState<unknown[]>([]);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [corrigiendo, setCorrigiendo] = useState(false);

  useEffect(() => {
    setExamen(null);
    setError(null);
    setRespuestas([]);
    setResultado(null);
    traerExamen(opciones)
      .then(setExamen)
      .catch((e) => setError(String(e.message ?? e)));
  }, [opciones]);

  // La corrección la hace siempre el backend: regenera el examen desde la
  // semilla y compara. Así no hay una segunda implementación en el frontend.
  const corregir = useCallback(async () => {
    if (!examen) return;
    setCorrigiendo(true);
    try {
      const r = await pedirCorreccion({ ...opciones, semilla: examen.semilla }, respuestas);
      setResultado(r);
    } catch (e) {
      setError(String((e as Error).message ?? e));
    } finally {
      setCorrigiendo(false);
    }
  }, [examen, opciones, respuestas]);

  const ejercicio = examen?.ejercicios[indice] ?? null;
  const totalPasos = ejercicio?.pasos?.length ?? 0;

  const irA = useCallback(
    (nuevo: number) => {
      if (!examen) return;
      setIndice(Math.max(0, Math.min(examen.ejercicios.length - 1, nuevo)));
      setPaso(0);
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
    [examen],
  );

  // Flechas para moverse entre pasos sin sacar las manos del teclado.
  useEffect(() => {
    function tecla(e: KeyboardEvent) {
      if (e.target instanceof HTMLInputElement) return;
      if (e.key === "ArrowRight") setPaso((p) => Math.min(totalPasos - 1, p + 1));
      if (e.key === "ArrowLeft") setPaso((p) => Math.max(0, p - 1));
    }
    window.addEventListener("keydown", tecla);
    return () => window.removeEventListener("keydown", tecla);
  }, [totalPasos]);

  if (error) {
    return (
      <main className="mx-auto max-w-2xl px-5 py-20">
        <h1 className="text-2xl">No se pudo generar el examen</h1>
        <p className="mt-3" style={{ color: "var(--color-mal)" }}>
          {error}
        </p>
        <p className="mt-4 text-sm" style={{ color: "var(--color-suave)" }}>
          Si estás en local, revisá que el backend esté corriendo:{" "}
          <code>npm run dev:api</code>
        </p>
        <Link href="/" className="mt-6 inline-block underline">
          Volver
        </Link>
      </main>
    );
  }

  if (!examen || !ejercicio) {
    return (
      <main className="mx-auto max-w-2xl px-5 py-20 text-center" style={{ color: "var(--color-suave)" }}>
        Generando el examen…
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-[1180px] px-5 py-8">
      <header className="no-imprimir mb-8 flex flex-wrap items-center gap-x-5 gap-y-2">
        <Link href="/" className="chip" style={{ color: "var(--color-acento)" }}>
          ← Inicio
        </Link>
        <h1 className="text-lg font-semibold">{examen.titulo}</h1>
        <span className="chip" style={{ color: "var(--color-suave)" }}>
          semilla {examen.semilla} · {examen.puntaje_total} puntos
        </span>
        <button
          onClick={() => window.print()}
          className="chip ml-auto rounded border px-3 py-1"
          style={{ borderColor: "var(--color-borde)", color: "var(--color-suave)" }}
        >
          Imprimir
        </button>
      </header>

      {/* Riel de ejercicios */}
      <nav className="no-imprimir mb-6 flex flex-wrap gap-1.5">
        {examen.ejercicios.map((e, i) => (
          <button
            key={i}
            onClick={() => irA(i)}
            title={e.subtema}
            className={clases(
              "size-8 rounded-lg border text-sm transition",
              i === indice && "font-bold",
            )}
            style={{
              borderColor: i === indice ? "var(--color-acento)" : "var(--color-borde)",
              background: i === indice ? "var(--color-acento-suave)" : "var(--color-superficie)",
              color: i === indice ? "var(--color-acento)" : "var(--color-suave)",
            }}
          >
            {i + 1}
          </button>
        ))}
      </nav>

      <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,26rem)]">
        {/* Columna del enunciado y la resolución */}
        <div>
          <p className="chip mb-1" style={{ color: "var(--color-acento)" }}>
            {ejercicio.tema} · {ejercicio.puntaje} pts
          </p>
          <h2 className="mb-4 text-2xl leading-snug">{ejercicio.subtema}</h2>

          <div
            className="rounded-xl border p-4"
            style={{ background: "var(--color-superficie)", borderColor: "var(--color-borde)" }}
          >
            <Markdown texto={ejercicio.consigna} />
          </div>

          <Practica
            practica={ejercicio.practica}
            conSoluciones={examen.con_soluciones}
            respuesta={respuestas[indice]}
            onCambio={(valor) =>
              setRespuestas((previas) => {
                const copia = [...previas];
                copia[indice] = valor;
                return copia;
              })
            }
            detalle={resultado?.ejercicios[indice]?.detalle}
          />

          <div className="no-imprimir mt-4 flex flex-wrap items-center gap-4">
            <button
              onClick={corregir}
              disabled={corrigiendo}
              className="rounded-lg px-5 py-2 text-sm font-medium text-white disabled:opacity-50"
              style={{ background: "var(--color-acento)" }}
            >
              {corrigiendo ? "Corrigiendo…" : "Corregir"}
            </button>
            {resultado && (
              (() => {
                const aqui = resultado.ejercicios[indice];
                const perfecto = aqui && aqui.total > 0 && aqui.aciertos === aqui.total;
                return (
                  <span className="text-sm">
                    {/* El puntaje global va en color neutro salvo que esté
                        aprobado: pintarlo de rojo mientras faltan ejercicios por
                        contestar da la impresión de haber errado algo. */}
                    <strong
                      style={{
                        color: resultado.aprobado ? "var(--color-bien)" : "var(--color-tinta)",
                      }}
                    >
                      {resultado.puntos} / {resultado.puntos_totales}
                    </strong>{" "}
                    en todo el examen · en este ejercicio{" "}
                    <strong style={{ color: perfecto ? "var(--color-bien)" : "var(--color-mal)" }}>
                      {aqui?.aciertos ?? 0}/{aqui?.total ?? 0}
                    </strong>
                  </span>
                );
              })()
            )}
          </div>

          {ejercicio.pasos && ejercicio.pasos.length > 0 && (
            <section className="mt-10">
              <h3 className="chip mb-3" style={{ color: "var(--color-suave)" }}>
                Resolución paso a paso
              </h3>
              <ol className="space-y-2">
                {ejercicio.pasos.map((p, i) => {
                  const abierto = i === paso;
                  return (
                    <li key={i}>
                      <button
                        onClick={() => setPaso(i)}
                        className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition"
                        style={{
                          background: abierto ? "var(--color-acento-suave)" : "transparent",
                        }}
                      >
                        <span
                          className="grid size-6 shrink-0 place-items-center rounded-full text-[0.72rem] font-bold"
                          style={{
                            background: abierto ? "var(--color-acento)" : "var(--color-borde)",
                            color: abierto ? "#fff" : "var(--color-suave)",
                          }}
                        >
                          {i + 1}
                        </span>
                        <span className={clases("flex-1", abierto && "font-semibold")}>
                          {p.titulo}
                        </span>
                      </button>
                      {abierto && (
                        <div className="pl-12 pr-2 text-[0.97rem]">
                          <Markdown texto={p.detalle} />
                        </div>
                      )}
                    </li>
                  );
                })}
              </ol>
              <p className="no-imprimir mt-3 text-[0.8rem]" style={{ color: "var(--color-suave)" }}>
                Se puede avanzar con las flechas ← →
              </p>
            </section>
          )}

          {ejercicio.respuesta && (
            <section
              className="mt-8 rounded-xl border-l-4 p-4"
              style={{ borderColor: "var(--color-acento)", background: "var(--color-superficie)" }}
            >
              <h3 className="chip mb-1" style={{ color: "var(--color-acento)" }}>
                Respuesta
              </h3>
              <Markdown texto={ejercicio.respuesta} />
            </section>
          )}

          {ejercicio.observacion && (
            <section className="mt-6">
              <h3 className="chip mb-1" style={{ color: "var(--color-suave)" }}>
                Por qué · errores típicos
              </h3>
              <div style={{ color: "var(--color-suave)" }}>
                <Markdown texto={ejercicio.observacion} />
              </div>
            </section>
          )}

          {ejercicio.verificacion && (
            <p className="mt-6 text-[0.82rem]" style={{ color: "var(--color-suave)" }}>
              ✔ Verificación automática: {ejercicio.verificacion}
            </p>
          )}

          <div className="no-imprimir mt-10 flex justify-between">
            <button
              onClick={() => irA(indice - 1)}
              disabled={indice === 0}
              className="rounded-lg border px-4 py-2 text-sm disabled:opacity-30"
              style={{ borderColor: "var(--color-borde)" }}
            >
              ← Anterior
            </button>
            <button
              onClick={() => irA(indice + 1)}
              disabled={indice === examen.ejercicios.length - 1}
              className="rounded-lg px-4 py-2 text-sm text-white disabled:opacity-30"
              style={{ background: "var(--color-acento)" }}
            >
              Siguiente →
            </button>
          </div>
        </div>

        {/* Columna del visual, que acompaña el paso activo */}
        <aside className="lg:sticky lg:top-8 lg:self-start">
          <Visual visual={ejercicio.visual} paso={paso} totalPasos={totalPasos} />
        </aside>
      </div>
    </main>
  );
}

export default function PaginaExamen() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto max-w-2xl px-5 py-20 text-center" style={{ color: "var(--color-suave)" }}>
          Cargando…
        </main>
      }
    >
      <Contenido />
    </Suspense>
  );
}
