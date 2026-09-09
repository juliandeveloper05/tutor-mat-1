"use client";

import katex from "katex";
import { useMemo } from "react";

/**
 * Renderiza LaTeX con KaTeX.
 *
 * El backend manda cada fórmula en dos formatos (`texto` en Unicode y `latex`).
 * Si KaTeX falla por lo que sea, se muestra el texto plano: nunca se rompe la
 * página por una fórmula.
 */
export function Mate({
  latex,
  texto,
  display = false,
  className,
}: {
  latex: string;
  texto?: string;
  display?: boolean;
  className?: string;
}) {
  const html = useMemo(() => {
    try {
      return katex.renderToString(latex, {
        displayMode: display,
        throwOnError: false,
        output: "html",
      });
    } catch {
      return null;
    }
  }, [latex, display]);

  if (html === null) {
    return <span className={className}>{texto ?? latex}</span>;
  }
  return (
    <span
      className={className}
      // KaTeX genera el marcado; la entrada viene del backend, no del usuario.
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
