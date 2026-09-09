"use client";

import { Html, Line, OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Component, type ReactNode, useMemo } from "react";
import * as THREE from "three";
import type { VisualHasse } from "../../lib/tipos";

/**
 * Diagrama de Hasse en 3D.
 *
 * Cuando el orden es el de inclusión sobre P(A) con #A = 3, los vértices se
 * ubican en las coordenadas exactas del cubo: cada subconjunto va en (b₀,b₁,b₂)
 * según qué elementos contiene, así que **el diagrama es literalmente el cubo**
 * y cada arista corresponde a agregar un elemento.
 *
 * Después se rota el conjunto para que la diagonal (1,1,1) —la dirección en la
 * que crece la inclusión— apunte hacia arriba. De esa forma se lee como un
 * Hasse normal (abajo lo chico, arriba lo grande) sin dejar de ser el cubo:
 * girándolo con el mouse se ve una cosa o la otra.
 *
 * Para órdenes cualesquiera no hay un cubo que valga, así que se usa el layout
 * clásico por niveles: la altura es el nivel y dentro de cada nivel los nodos
 * se reparten en círculo.
 */

const ESCALA = 2.2;
const ALTURA_NIVEL = 1.7;

function posiciones(v: VisualHasse): Record<string, THREE.Vector3> {
  const salida: Record<string, THREE.Vector3> = {};

  if (v.bits && v.base && v.base.length === 3) {
    for (const e of v.elems) {
      const [x, y, z] = v.bits[e];
      salida[e] = new THREE.Vector3(
        (Number(x) - 0.5) * ESCALA,
        (Number(y) - 0.5) * ESCALA,
        (Number(z) - 0.5) * ESCALA,
      );
    }
    return salida;
  }

  // Layout por niveles.
  const porNivel = new Map<number, string[]>();
  for (const e of v.elems) {
    const n = v.nivel[e] ?? 0;
    porNivel.set(n, [...(porNivel.get(n) ?? []), e]);
  }
  const alturaMax = Math.max(...porNivel.keys());
  for (const [nivel, elementos] of porNivel) {
    const y = (nivel - alturaMax / 2) * ALTURA_NIVEL;
    elementos.forEach((e, i) => {
      if (elementos.length === 1) {
        salida[e] = new THREE.Vector3(0, y, 0);
        return;
      }
      const angulo = (i / elementos.length) * Math.PI * 2;
      const radio = 1.15 + elementos.length * 0.14;
      salida[e] = new THREE.Vector3(
        Math.cos(angulo) * radio,
        y,
        Math.sin(angulo) * radio,
      );
    });
  }
  return salida;
}

/** Rotación que lleva la diagonal del cubo a la vertical. */
function rotacionDelCubo(v: VisualHasse): THREE.Euler {
  if (!(v.bits && v.base && v.base.length === 3)) return new THREE.Euler(0, 0, 0);
  const q = new THREE.Quaternion().setFromUnitVectors(
    new THREE.Vector3(1, 1, 1).normalize(),
    new THREE.Vector3(0, 1, 0),
  );
  return new THREE.Euler().setFromQuaternion(q);
}

function Escena({
  visual,
  resaltados,
}: {
  visual: VisualHasse;
  resaltados: Set<string>;
}) {
  const pos = useMemo(() => posiciones(visual), [visual]);
  const rotacion = useMemo(() => rotacionDelCubo(visual), [visual]);
  const hayResaltados = resaltados.size > 0;

  return (
    <group rotation={rotacion}>
      {visual.hasse.map(([x, y], i) => {
        const destacada = resaltados.has(x) && resaltados.has(y);
        return (
          <Line
            key={`${x}-${y}-${i}`}
            points={[pos[x], pos[y]]}
            color={destacada ? "#6d4aff" : "#8a8f9c"}
            lineWidth={destacada ? 2.6 : 1.3}
            transparent
            opacity={hayResaltados && !destacada ? 0.3 : 0.85}
          />
        );
      })}

      {visual.elems.map((e) => {
        const destacado = resaltados.has(e);
        return (
          <group key={e} position={pos[e]}>
            <mesh>
              <sphereGeometry args={[destacado ? 0.17 : 0.12, 24, 24]} />
              <meshStandardMaterial
                color={destacado ? "#6d4aff" : "#9aa0ad"}
                emissive={destacado ? "#6d4aff" : "#000000"}
                emissiveIntensity={destacado ? 0.45 : 0}
                roughness={0.4}
              />
            </mesh>
            {/* La etiqueta se contra-rota para que no quede dada vuelta. */}
            <Html
              center
              distanceFactor={9}
              style={{ pointerEvents: "none", userSelect: "none" }}
            >
              <span
                style={{
                  fontFamily: "var(--font-codigo)",
                  fontSize: "13px",
                  whiteSpace: "nowrap",
                  padding: "1px 6px",
                  borderRadius: "6px",
                  background: "var(--color-superficie)",
                  border: "1px solid var(--color-borde)",
                  color: destacado ? "var(--color-acento)" : "var(--color-tinta)",
                  fontWeight: destacado ? 700 : 500,
                  opacity: hayResaltados && !destacado ? 0.45 : 1,
                }}
              >
                {visual.etiquetas[e] ?? e}
              </span>
            </Html>
          </group>
        );
      })}
    </group>
  );
}

class LimiteDeError extends Component<
  { children: ReactNode; alternativa: ReactNode },
  { falló: boolean }
> {
  state = { falló: false };
  static getDerivedStateFromError() {
    return { falló: true };
  }
  render() {
    return this.state.falló ? this.props.alternativa : this.props.children;
  }
}

/** Si no hay WebGL, el diagrama por niveles en texto dice lo mismo. */
function PorNiveles({ visual }: { visual: VisualHasse }) {
  const niveles = new Map<number, string[]>();
  for (const e of visual.elems) {
    const n = visual.nivel[e] ?? 0;
    niveles.set(n, [...(niveles.get(n) ?? []), e]);
  }
  const orden = [...niveles.keys()].sort((a, b) => b - a);
  return (
    <pre
      className="overflow-x-auto rounded-lg border p-4 text-sm"
      style={{
        background: "var(--color-superficie)",
        borderColor: "var(--color-borde)",
        fontFamily: "var(--font-codigo)",
      }}
    >
      {orden
        .map(
          (n) =>
            `nivel ${n}:  ${(niveles.get(n) ?? [])
              .map((e) => visual.etiquetas[e] ?? e)
              .join("   ")}`,
        )
        .join("\n")}
    </pre>
  );
}

export function Hasse3D({
  visual,
  resaltados = [],
  alto = 340,
}: {
  visual: VisualHasse;
  resaltados?: string[];
  alto?: number;
}) {
  const conjunto = useMemo(() => new Set(resaltados), [resaltados]);
  const esCubo = Boolean(visual.bits && visual.base?.length === 3);

  return (
    <LimiteDeError alternativa={<PorNiveles visual={visual} />}>
      <div
        className="overflow-hidden rounded-xl border"
        style={{ height: alto, borderColor: "var(--color-borde)", background: "var(--color-superficie)" }}
      >
        <Canvas camera={{ position: [3.4, 2.4, 4.6], fov: 46 }} dpr={[1, 2]}>
          <ambientLight intensity={0.85} />
          <directionalLight position={[4, 6, 3]} intensity={1.1} />
          <Escena visual={visual} resaltados={conjunto} />
          <OrbitControls enablePan={false} minDistance={3} maxDistance={12} />
        </Canvas>
      </div>
      <p className="mt-2 text-[0.8rem]" style={{ color: "var(--color-suave)" }}>
        Se puede girar con el mouse.{" "}
        {esCubo
          ? "Los ocho subconjuntos son los vértices de un cubo: cada arista agrega un elemento."
          : "La altura es el nivel: se sube por las líneas para leer la relación."}
      </p>
    </LimiteDeError>
  );
}
