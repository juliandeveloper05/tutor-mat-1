"use client";

import { clases } from "../lib/formato";
import { Mate } from "./Mate";
import type { DetalleItem, Practica as TipoPractica } from "../lib/tipos";

/**
 * Formulario para contestar el ejercicio.
 *
 * Sólo dibuja y recoge la respuesta: **no corrige**. La corrección la hace
 * siempre el backend (`POST /api/corregir`), incluso en modo estudio, para que
 * no exista una segunda implementación en TypeScript que se pueda desviar de la
 * de Python —que es la que está testeada—.
 */

export function Practica({
  practica,
  respuesta,
  onCambio,
  detalle,
}: {
  practica: TipoPractica;
  conSoluciones?: boolean;
  respuesta?: unknown;
  onCambio?: (valor: unknown) => void;
  detalle?: DetalleItem[];
}) {
  if (!practica?.tipo) return null;
  const editable = Boolean(onCambio);
  const marca = (i: number) => detalle?.[i];

  function actualizarLista(indice: number, valor: unknown) {
    const actual = Array.isArray(respuesta) ? [...respuesta] : [];
    actual[indice] = valor;
    onCambio?.(actual);
  }

  function actualizarObjeto(clave: string, valor: unknown) {
    const actual =
      respuesta && typeof respuesta === "object" && !Array.isArray(respuesta)
        ? { ...(respuesta as Record<string, unknown>) }
        : {};
    actual[clave] = valor;
    onCambio?.(actual);
  }

  const lista = Array.isArray(respuesta) ? respuesta : [];
  const objeto =
    respuesta && typeof respuesta === "object" && !Array.isArray(respuesta)
      ? (respuesta as Record<string, unknown>)
      : {};

  return (
    <section
      className="no-imprimir mt-6 rounded-xl border p-4"
      style={{ borderColor: "var(--color-borde)", background: "var(--color-superficie)" }}
    >
      <h3 className="chip mb-3" style={{ color: "var(--color-acento)" }}>
        Contestá vos
      </h3>

      {practica.tipo === "opcion-multiple" && (
        <div>
          <p className="mb-2">{practica.pregunta}</p>
          <Opciones
            opciones={practica.opciones}
            elegida={typeof respuesta === "number" ? respuesta : null}
            onElegir={(i) => onCambio?.(i)}
            editable={editable}
            marca={marca(0)}
          />
        </div>
      )}

      {practica.tipo === "verdadero-falso" && (
        <ul className="space-y-2">
          {practica.items.map((item, i) => (
            <li key={i} className="flex flex-wrap items-center justify-between gap-3">
              <span className="mate flex-1">{item.enunciado}</span>
              <div className="flex gap-1">
                {[true, false].map((v) => (
                  <button
                    key={String(v)}
                    disabled={!editable}
                    onClick={() => actualizarLista(i, v)}
                    className="w-10 rounded-lg border py-1 text-sm"
                    style={estiloBoton(lista[i] === v, marca(i))}
                  >
                    {v ? "V" : "F"}
                  </button>
                ))}
              </div>
              <Veredicto item={marca(i)} />
            </li>
          ))}
        </ul>
      )}

      {practica.tipo === "numerica" && (
        <ul className="space-y-3">
          {practica.items.map((item, i) => (
            <li key={i}>
              <p className="mb-1 text-[0.94rem]">{item.texto}</p>
              <div className="flex items-center gap-3">
                <input
                  disabled={!editable}
                  inputMode="numeric"
                  value={(lista[i] as string) ?? ""}
                  onChange={(e) => actualizarLista(i, e.target.value.replace(/[^\d-]/g, ""))}
                  className="w-28 rounded-lg border px-3 py-1.5"
                  style={{
                    borderColor: marca(i)
                      ? marca(i)!.correcto
                        ? "var(--color-bien)"
                        : "var(--color-mal)"
                      : "var(--color-borde)",
                    background: "var(--color-papel)",
                    fontFamily: "var(--font-codigo)",
                  }}
                />
                <code className="text-[0.82rem]" style={{ color: "var(--color-suave)" }}>
                  {item.expresion}
                </code>
                <Veredicto item={marca(i)} />
              </div>
            </li>
          ))}
        </ul>
      )}

      {(practica.tipo === "nombrar-ley" || practica.tipo === "nombrar-regla") && (
        <ol className="space-y-3">
          {practica.items.map((item, i) => (
            <li key={i}>
              <p className="mb-1 text-[0.9rem]" style={{ color: "var(--color-suave)" }}>
                Paso {item.n ?? i + 1}
                {(item.despues ?? item.formula) && (
                  <>
                    {" · "}
                    <Mate
                      latex={(item.despues ?? item.formula)!.latex}
                      texto={(item.despues ?? item.formula)!.texto}
                    />
                  </>
                )}
              </p>
              <select
                disabled={!editable}
                value={typeof lista[i] === "number" ? String(lista[i]) : ""}
                onChange={(e) => actualizarLista(i, Number(e.target.value))}
                className="w-full rounded-lg border px-3 py-1.5 text-sm"
                style={{
                  borderColor: marca(i)
                    ? marca(i)!.correcto
                      ? "var(--color-bien)"
                      : "var(--color-mal)"
                    : "var(--color-borde)",
                  background: "var(--color-papel)",
                }}
              >
                <option value="">— elegir la ley aplicada —</option>
                {item.opciones.map((o, j) => (
                  <option key={j} value={j}>
                    {o}
                  </option>
                ))}
              </select>
            </li>
          ))}
        </ol>
      )}

      {practica.tipo === "propiedades" && (
        <div className="flex flex-wrap gap-2">
          {practica.propiedades.map((nombre, i) => {
            const activa = objeto[nombre] === true;
            return (
              <button
                key={nombre}
                disabled={!editable}
                onClick={() => actualizarObjeto(nombre, !activa)}
                className="rounded-full border px-4 py-1.5 text-sm capitalize"
                style={estiloBoton(activa, marca(i))}
              >
                {nombre}
              </button>
            );
          })}
          <p className="mt-1 w-full text-[0.8rem]" style={{ color: "var(--color-suave)" }}>
            Marcá las que cumple. Las que dejes sin marcar cuentan como que no las cumple.
          </p>
        </div>
      )}

      {practica.tipo === "si-no" && (
        <div className="flex flex-wrap items-center gap-3">
          <span className="flex-1">{practica.pregunta}</span>
          {[true, false].map((v) => (
            <button
              key={String(v)}
              disabled={!editable}
              onClick={() => onCambio?.(v)}
              className="rounded-lg border px-4 py-1.5 text-sm"
              style={estiloBoton(respuesta === v, marca(0))}
            >
              {v ? "Sí" : "No"}
            </button>
          ))}
          <Veredicto item={marca(0)} />
        </div>
      )}

      {practica.tipo === "elementos-particulares" && (
        <ul className="space-y-2">
          {practica.preguntas.map((pregunta, i) => (
            <li key={pregunta.clave} className="flex flex-wrap items-center gap-3">
              <span className="w-32">{pregunta.texto}</span>
              <select
                disabled={!editable}
                value={(objeto[pregunta.clave] as string) ?? "__nada__"}
                onChange={(e) =>
                  actualizarObjeto(
                    pregunta.clave,
                    e.target.value === "__nada__" ? null : e.target.value,
                  )
                }
                className="rounded-lg border px-3 py-1.5 text-sm"
                style={{
                  borderColor: marca(i)
                    ? marca(i)!.correcto
                      ? "var(--color-bien)"
                      : "var(--color-mal)"
                    : "var(--color-borde)",
                  background: "var(--color-papel)",
                }}
              >
                <option value="__nada__">no tiene</option>
                {practica.opciones.map((e) => (
                  <option key={e} value={e}>
                    {practica.etiquetas[e] ?? e}
                  </option>
                ))}
              </select>
              <Veredicto item={marca(i)} etiquetas={practica.etiquetas} />
            </li>
          ))}
        </ul>
      )}

      {practica.tipo === "conjuntos-por-extension" && (
        <ul className="space-y-2">
          {practica.campos.map((campo, i) => (
            <li key={campo} className="flex items-center gap-3">
              <span className="w-6 font-semibold">{campo} =</span>
              <input
                disabled={!editable}
                placeholder="1, 2, 5"
                value={(objeto[campo] as string) ?? ""}
                onChange={(e) => actualizarObjeto(campo, e.target.value)}
                className="flex-1 rounded-lg border px-3 py-1.5"
                style={{
                  borderColor: marca(i)
                    ? marca(i)!.correcto
                      ? "var(--color-bien)"
                      : "var(--color-mal)"
                    : "var(--color-borde)",
                  background: "var(--color-papel)",
                  fontFamily: "var(--font-codigo)",
                }}
              />
              <Veredicto item={marca(i)} />
            </li>
          ))}
        </ul>
      )}

      {practica.tipo === "emparejar" && (
        <ul className="space-y-2">
          <p className="text-[0.9rem]" style={{ color: "var(--color-suave)" }}>
            {practica.consigna}
          </p>
          {practica.izquierda.map((izq, i) => (
            <li key={i} className="flex flex-wrap items-center gap-3">
              <code className="flex-1 text-[0.88rem]">{izq}</code>
              <select
                disabled={!editable}
                value={(lista[i] as string) ?? ""}
                onChange={(e) => actualizarLista(i, e.target.value)}
                className="rounded-lg border px-3 py-1.5 text-sm"
                style={{
                  borderColor: marca(i)
                    ? marca(i)!.correcto
                      ? "var(--color-bien)"
                      : "var(--color-mal)"
                    : "var(--color-borde)",
                  background: "var(--color-papel)",
                  fontFamily: "var(--font-codigo)",
                }}
              >
                <option value="">— dominio —</option>
                {practica.derecha.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
              <Veredicto item={marca(i)} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function Opciones({
  opciones,
  elegida,
  onElegir,
  editable,
  marca,
}: {
  opciones: string[];
  elegida: number | null;
  onElegir: (i: number) => void;
  editable: boolean;
  marca?: DetalleItem;
}) {
  return (
    <div className="grid gap-1.5 sm:grid-cols-2">
      {opciones.map((o, i) => (
        <button
          key={i}
          disabled={!editable}
          onClick={() => onElegir(i)}
          className="rounded-lg border px-3 py-2 text-left text-sm"
          style={estiloBoton(elegida === i, elegida === i ? marca : undefined)}
        >
          <span style={{ fontFamily: "var(--font-codigo)" }}>{o}</span>
        </button>
      ))}
    </div>
  );
}

function estiloBoton(activo: boolean, marca?: DetalleItem) {
  if (marca && activo) {
    return {
      borderColor: marca.correcto ? "var(--color-bien)" : "var(--color-mal)",
      background: marca.correcto ? "var(--color-bien)" : "var(--color-mal)",
      color: "#fff",
    };
  }
  return {
    borderColor: activo ? "var(--color-acento)" : "var(--color-borde)",
    background: activo ? "var(--color-acento)" : "var(--color-papel)",
    color: activo ? "#fff" : "var(--color-tinta)",
  };
}

function Veredicto({
  item,
  etiquetas,
}: {
  item?: DetalleItem;
  /** Traduce claves internas a lo que ve el alumno: s7 → {a, b, c}. */
  etiquetas?: Record<string, string>;
}) {
  if (!item) return null;
  const esperado = formatear(item.esperado, etiquetas);
  return (
    // Sin .chip: pasaría a mayúsculas, y en {a, b, c} eso cambia los elementos.
    <span
      className="text-[0.78rem] font-semibold whitespace-nowrap"
      style={{ color: item.correcto ? "var(--color-bien)" : "var(--color-mal)" }}
      title={item.correcto ? undefined : `Correcta: ${esperado}`}
    >
      {item.correcto ? "✔" : `✕ ${esperado}`}
    </span>
  );
}

function formatear(valor: unknown, etiquetas?: Record<string, string>): string {
  if (valor === null || valor === undefined) return "no tiene";
  if (typeof valor === "boolean") return valor ? "V" : "F";
  if (Array.isArray(valor)) {
    return valor.map((v) => formatear(v, etiquetas)).join(", ");
  }
  const texto = String(valor);
  return etiquetas?.[texto] ?? texto;
}
