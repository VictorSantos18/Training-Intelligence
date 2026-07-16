import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Training Intelligence",
  description: "Personal training intelligence system for calisthenics progress tracking.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}

