import type { Metadata } from "next";
import "katex/dist/katex.min.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "Integradores — Matemática I",
  description:
    "Generador visual de exámenes integradores de Matemática I (TUPI/UNQ), con la resolución explicada paso a paso.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
