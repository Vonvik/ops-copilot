// app/page.tsx
import { apiGet } from "@/lib/api";
import { ProcessedListSchema } from "@/types/processed";
import type { ProcessedItem } from "@/types/processed";
import ProcessedForm from "@/components/processed-form"; // ⬅️ formulario (client component)

// Helpers de presentación
function fmtAmount(v: number | null | undefined) {
  if (v === null || v === undefined) return "—";
  return Number.isFinite(v) ? v : "—";
}

function fmtDate(s: string | null | undefined) {
  if (!s) return "—";
  return s; // si luego te llega ISO: return new Date(s).toLocaleDateString();
}

// Chip de confianza IA
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

// Chip de estado de revisión
function reviewStatusLabel(status: ProcessedItem["review_status"]) {
  if (!status) return "—";
  if (status === "pending") return "Pendiente";
  if (status === "approved") return "Aprobado";
  if (status === "rejected") return "Rechazado";
  return status;
}

function reviewStatusClass(status: ProcessedItem["review_status"]) {
  if (!status) return "bg-gray-100 text-gray-700";
  if (status === "pending") return "bg-yellow-100 text-yellow-800";
  if (status === "approved") return "bg-green-100 text-green-800";
  if (status === "rejected") return "bg-red-100 text-red-800";
  return "bg-gray-100 text-gray-700";
}

// Forzamos render dinámico (sin cache) en Next 16
export const dynamic = "force-dynamic";

async function getProcessed(): Promise<{ data: ProcessedItem[]; error: string | null }> {
  try {
    // NO pongas /api/v1 aquí si tu NEXT_PUBLIC_API_URL ya lo incluye
    const raw = await apiGet<unknown>("/processed?limit=20");
    const parsed = ProcessedListSchema.safeParse(raw);

    if (!parsed.success) {
      return {
        data: [],
        error: "Respuesta de API con formato inesperado (validación fallida).",
      };
    }

    // Normaliza created_at si falta, usando date_str o ahora mismo.
    const normalized = parsed.data.map((item: any) => ({
      ...item,
      created_at: item?.created_at ?? item?.date_str ?? new Date().toISOString(),
    }));

    return { data: normalized as ProcessedItem[], error: null };
  } catch (e: any) {
    return { data: [], error: e?.message ?? "Error al cargar datos" };
  }
}

export default async function DashboardPage() {
  const { data, error } = await getProcessed();

  return (
    <section className="space-y-4 p-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <p className="text-sm text-gray-500">
        Lista completa de gastos + creación manual. La IA marca confianza y estado de revisión.
      </p>

      {/* GRID: izquierda tabla, derecha formulario */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Columna 1: tabla */}
        <div className="rounded border bg-white overflow-hidden">
          {error ? (
            <div className="p-3 text-red-700 bg-red-50 border-b border-red-200">
              {error}
            </div>
          ) : null}

          {!error && (
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-3 py-2">ID</th>
                  <th className="text-left px-3 py-2">Concepto</th>
                  <th className="text-left px-3 py-2">Importe</th>
                  <th className="text-left px-3 py-2">Fecha</th>
                  <th className="text-left px-3 py-2">Tipo de entrada</th>
                  <th className="text-left px-3 py-2">IA</th>
                  <th className="text-left px-3 py-2">Estado</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row) => (
                  <tr key={row.id} className="border-t">
                    <td className="px-3 py-2">{row.id}</td>
                    <td className="px-3 py-2">{row.item ?? "—"}</td>
                    <td className="px-3 py-2">{fmtAmount(row.amount)}</td>
                    <td className="px-3 py-2">{fmtDate(row.date_str)}</td>
                    <td className="px-3 py-2">{row.source_file ?? "—"}</td>

                    {/* Confianza IA */}
                    <td className="px-3 py-2">
                      {row.nlp_overall_confidence != null ? (
                        <span
                          className={
                            "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium " +
                            iaConfidenceClass(row.nlp_overall_confidence)
                          }
                        >
                          {iaConfidenceLabel(row.nlp_overall_confidence)}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">—</span>
                      )}
                    </td>

                    {/* Estado revisión */}
                    <td className="px-3 py-2">
                      <span
                        className={
                          "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium " +
                          reviewStatusClass(row.review_status ?? null)
                        }
                      >
                        {reviewStatusLabel(row.review_status ?? null)}
                      </span>
                    </td>
                  </tr>
                ))}

                {data.length === 0 && (
                  <tr>
                    <td className="px-3 py-6 text-center text-gray-500" colSpan={7}>
                      Sin datos
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>

        {/* Columna 2: formulario */}
        <div className="rounded border bg-white p-4">
          <h2 className="mb-3 text-lg font-semibold">Nuevo registro</h2>
          {/* El formulario es client component; no pasamos funciones desde el server component */}
          <ProcessedForm />
        </div>
      </div>
    </section>
  );
}
