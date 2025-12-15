import type { Metadata } from "next";
import type { ReactNode } from "react";

import Providers from "@/components/Providers";                 // SessionProvider dentro (client)
import QueryProvider from "@/components/providers/query-provider"; // React Query (client)

import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";                      // client
import { Toaster } from "@/components/ui/sonner";

import "./globals.css";

export const metadata: Metadata = {
  title: "Ops-Copilot",
  description: "Frontend (Fase 2)",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        {/* Contextos globales: NextAuth + React Query */}
        <Providers>
          <QueryProvider>
            {/* Layout general: header arriba (altura auto), luego sidebar + contenido */}
            <div className="grid min-h-screen grid-cols-[15rem_1fr] grid-rows-[auto_1fr]">
              {/* Fila 1 (auto), columna 1-2: Header + Navbar */}
              <header className="col-span-2 border-b bg-white">
                <Header />
                <Navbar />
              </header>

              {/* Fila 2, col 1: Sidebar */}
              <aside className="border-r bg-white">
                <Sidebar />
              </aside>

              {/* Fila 2, col 2: Contenido principal */}
              <main
                className="p-6 overflow-x-auto"
                role="main"
                aria-label="Contenido principal"
              >
                {children}
              </main>
            </div>

            {/* Toaster global (avisos) */}
            <Toaster position="top-right" />
          </QueryProvider>
        </Providers>
      </body>
    </html>
  );
}
