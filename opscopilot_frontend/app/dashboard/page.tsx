// src/app/dashboard/page.tsx
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import Link from "next/link";

import { apiGet, getPendingProcessed } from "@/lib/api";
import type { ProcessedItem } from "@/types/processed";
import NewExpenseForm from "@/components/processed/NewExpenseForm";

import { getProcessedStats } from "@/lib/api";
import type { ProcessedStats } from "@/lib/api";

// Helper para color de confianza IA
function iaConfidenceClass(conf?: number | null) {
  if (conf == null) return "bg-gray-100 text-gray-700";
  if (conf >= 0.8) return "bg-green-100 text-green-800";
  if (conf >= 0.4) return "bg-yellow-100 text-yellow-800";
  return "bg-red-100 text-red-800";
}

function iaConfidenceLabel(conf?: number | null) {
  if (conf == null) return "-";
  return `${Math.round(conf * 100)}%`;
}

async function getProcessed(): Promise<ProcessedItem[]> {
  // ejemplo real a tu FastAPI: /api/v1/processed?limit=10
  return apiGet<ProcessedItem[]>("/processed?limit=10");
}

async function loadDashboardStats(): Promise<ProcessedStats> {
  return getProcessedStats();
}

export default async function DashboardPage() {
  const session = await getServerSession(authOptions);
  const stats = await loadDashboardStats();


  // Safety extra por si alguien llega sin pasar por el middleware
  if (!session) {
    return (
      <div className="space-y-2 p-6">
        <h1 className="text-xl font-semibold">Dashboard</h1>
        <p className="text-sm text-gray-600">No autenticado.</p>
        <Link href="/auth/login" className="text-sm underline">
          Ir a login
        </Link>
      </div>
    );
  }

  const email = session.user?.email ?? "desconocido";
  // evitamos problemas de tipos con role
  const role = (session.user as any)?.role ?? "USER";

  // Últimos gastos
  const data = await getProcessed();
  // Pendientes de revisión (cola humana)
  const pending = await getPendingProcessed();
  const pendingCount = pending.length;

  return (
    <section className="space-y-6 p-6">
      {/* Cabecera: título + info usuario + resumen IA + botones */}
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div className="space-y-1">
          <h1 className="text-xl font-semibold">Dashboard</h1>
          <p>Bienvenido, {email}</p>
          <p className="text-sm text-gray-600">Rol: {role}</p>
        </div>

        <div className="flex flex-col gap-2 items-stretch md:items-end">
          {/* Resumen de revisión IA */}
          <div className="rounded-lg border bg-gray-50 px-3 py-2 text-sm">
            {pendingCount > 0 ? (
              <>
                <p>
                  Tienes{" "}
                  <span className="font-semibold">{pendingCount}</span> gastos
                  pendientes de revisión.
                </p>
                <Link
                  href="/dashboard/approvals"
                  className="mt-1 inline-flex items-center rounded-md border px-2 py-1 text-xs hover:bg-gray-100"
                >
                  Ir a revisión de gastos
                </Link>
              </>
            ) : (
              <p className="flex items-center gap-1">
                <span className="text-base">✅</span>
                <span>Todo revisado por ahora. Buen trabajo.</span>
              </p>
            )}
          </div>

          {/* Botones de navegación */}
          <div className="flex flex-wrap gap-2">
            <Link
              href="/dashboard/approvals"
              className="rounded-md border px-3 py-1.5 text-sm hover:bg-gray-50"
            >
              Ver aprobaciones pendientes
            </Link>

            <Link
              href="/dashboard/nlp"
              className="rounded-md border px-3 py-1.5 text-sm hover:bg-gray-50"
            >
              Monitor IA (NLP)
            </Link>

            <Link
              href="/dashboard/nlp/rules"
              className="rounded-md border px-3 py-1.5 text-sm hover:bg-gray-50"
            >
              Reglas IA
            </Link>

            <Link
              href="/"
              className="rounded-md border px-3 py-1.5 text-sm hover:bg-gray-50"
            >
              Ver lista completa
            </Link>
          </div>
        </div>
      </div>
            {/* Tarjetas de métricas IA */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mt-4">
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs font-medium uppercase text-gray-500">
            Gastos totales
          </p>
          <p className="mt-2 text-2xl font-semibold">{stats.total_count}</p>
        </div>

        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs font-medium uppercase text-gray-500">
            Procesados por IA
          </p>
          <p className="mt-2 text-2xl font-semibold">
            {stats.ia_count}
            <span className="ml-2 text-sm text-gray-500">
              {stats.total_count > 0
                ? `(${Math.round(
                    (stats.ia_count / stats.total_count) * 100,
                  )}%)`
                : ""}
            </span>
          </p>
        </div>

        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs font-medium uppercase text-gray-500">
            Pendientes de revisión
          </p>
          <p className="mt-2 text-2xl font-semibold">
            {stats.pending_review}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Usa la cola humana para vaciar este número.
          </p>
        </div>

        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs font-medium uppercase text-gray-500">
            Confianza media IA
          </p>
          <p className="mt-2 text-2xl font-semibold">
            {stats.avg_confidence != null
              ? `${Math.round(stats.avg_confidence * 100)}%`
              : "–"}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Basado solo en registros con IA.
          </p>
        </div>
      </div>

      {/* Formulario para crear nuevo gasto (NewExpenseForm) */}
      <NewExpenseForm />

      {/* Lista / tabla de últimos gastos procesados */}
      <div className="space-y-2">
        <h2 className="text-lg font-semibold">Últimos gastos procesados</h2>
        {data.length === 0 ? (
          <p className="text-sm text-gray-600">
            Todavía no hay registros procesados.
          </p>
        ) : (
          <ul className="space-y-1 text-sm">
            {data.map((item) => (
              <li key={item.id} className="rounded border px-2 py-1">
                <div className="flex items-center justify-between gap-2">
                  {/* Info principal del gasto */}
                  <div>
                    <span className="font-medium">
                      {item.item ?? "(sin concepto)"}
                    </span>{" "}
                    — {item.amount ?? 0} — {item.date_str ?? "sin fecha"} —{" "}
                    <span className="text-xs text-gray-600">
                      {item.source_file ?? "desconocido"}
                    </span>
                  </div>

                  {/* Badges IA / Manual + confianza */}
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-700">
                      {item.nlp_overall_confidence != null
                        ? "Origen: IA"
                        : "Origen: Manual"}
                    </span>

                    {item.nlp_overall_confidence != null && (
                      <span
                        className={
                          "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium " +
                          iaConfidenceClass(item.nlp_overall_confidence)
                        }
                      >
                        IA {iaConfidenceLabel(item.nlp_overall_confidence)}
                      </span>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Aquí después puedes meter más cosas: KPIs, gráficos, etc. */}
    </section>
  );
}
