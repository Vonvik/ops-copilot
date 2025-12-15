// app/dashboard/approvals/ApprovalsClient.tsx
"use client";

import { useMemo, useState } from "react";
import type { ProcessedItem } from "@/types/processed";
import { approveProcessed, rejectProcessed } from "@/lib/api";

type Props = {
  initialItems: ProcessedItem[];
};

type PendingProcessed = ProcessedItem & {
  nlp_overall_confidence?: number | null;
  needs_review?: boolean | null;
  review_status?: string | null;
};

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

export default function ApprovalsClient({ initialItems }: Props) {
  const [items, setItems] = useState<PendingProcessed[]>(initialItems);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [textFilter, setTextFilter] = useState("");
  const [minConf, setMinConf] = useState<number | "">("");
  const [loadingAction, setLoadingAction] = useState<"approve" | "reject" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      const text = textFilter.trim().toLowerCase();
      if (text) {
        const haystack = [
          item.item ?? "",
          item.source_file ?? "",
          item.date_str ?? "",
        ]
          .join(" ")
          .toLowerCase();

        if (!haystack.includes(text)) {
          return false;
        }
      }

      if (minConf !== "") {
        const conf = (item as any).nlp_overall_confidence as number | null | undefined;
        if (conf == null || conf < minConf) {
          return false;
        }
      }

      return true;
    });
  }, [items, textFilter, minConf]);

  const allVisibleSelected =
    filteredItems.length > 0 &&
    filteredItems.every((item) => selectedIds.includes(item.id));

  function toggleSelectAllVisible() {
    if (allVisibleSelected) {
      const visibleIds = filteredItems.map((i) => i.id);
      setSelectedIds((prev) => prev.filter((id) => !visibleIds.includes(id)));
    } else {
      const toAdd = filteredItems.map((i) => i.id);
      setSelectedIds((prev) => Array.from(new Set([...prev, ...toAdd])));
    }
  }

  function toggleRow(id: number) {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  }

  async function handleBatchAction(kind: "approve" | "reject") {
    if (selectedIds.length === 0) return;

    try {
      setLoadingAction(kind);
      setError(null);

      const ids = [...selectedIds];

      // Llamamos uno a uno; puedes optimizar a Promise.all si quieres
      for (const id of ids) {
        if (kind === "approve") {
          await approveProcessed(id);
        } else {
          await rejectProcessed(id);
        }
      }

      // Quitamos los ya procesados de la lista local
      setItems((prev) => prev.filter((item) => !ids.includes(item.id)));
      // Y limpiamos selección
      setSelectedIds((prev) => prev.filter((id) => !ids.includes(id)));
    } catch (err) {
      console.error(err);
      setError("Error al procesar la acción masiva. Revisa la consola o inténtalo de nuevo.");
    } finally {
      setLoadingAction(null);
    }
  }

  return (
    <div className="space-y-4">
      {/* Barra de filtros y acciones masivas */}
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div className="flex flex-col gap-2 md:flex-row md:items-end">
          <div className="space-y-1">
            <label className="block text-sm font-medium">Buscar</label>
            <input
              type="text"
              value={textFilter}
              onChange={(e) => setTextFilter(e.target.value)}
              placeholder="Concepto, fuente, fecha..."
              className="w-full rounded-md border px-3 py-2 text-sm md:w-64"
            />
          </div>

          <div className="space-y-1 md:ml-4">
            <label className="block text-sm font-medium">
              Confianza IA mínima (%)
            </label>
            <input
              type="number"
              min={0}
              max={100}
              value={minConf === "" ? "" : Math.round(minConf * 100)}
              onChange={(e) => {
                const v = e.target.value;
                if (v === "") {
                  setMinConf("");
                } else {
                  const num = Number(v);
                  if (!Number.isNaN(num)) {
                    setMinConf(Math.min(Math.max(num, 0), 100) / 100);
                  }
                }
              }}
              className="w-32 rounded-md border px-3 py-2 text-sm"
              placeholder="Ej. 60"
            />
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={selectedIds.length === 0 || loadingAction !== null}
            onClick={() => void handleBatchAction("approve")}
            className="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
          >
            {loadingAction === "approve"
              ? "Aprobando..."
              : `Aprobar seleccionados (${selectedIds.length})`}
          </button>
          <button
            type="button"
            disabled={selectedIds.length === 0 || loadingAction !== null}
            onClick={() => void handleBatchAction("reject")}
            className="inline-flex items-center rounded-md bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
          >
            {loadingAction === "reject"
              ? "Rechazando..."
              : `Rechazar seleccionados (${selectedIds.length})`}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}

      {/* Tabla */}
      <div className="overflow-x-auto rounded-lg border">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                <input
                  type="checkbox"
                  checked={allVisibleSelected}
                  onChange={toggleSelectAllVisible}
                  title="Select all visible items"
                  aria-label="Select all visible items"
                />
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                ID
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                Concepto
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                Importe
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                Fecha
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                Fuente
              </th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                Conf. IA
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {filteredItems.length === 0 ? (
              <tr>
                <td
                  colSpan={7}
                  className="px-3 py-4 text-center text-sm text-gray-500"
                >
                  No hay gastos pendientes que cumplan los filtros.
                </td>
              </tr>
            ) : (
              filteredItems.map((item) => {
                const conf =
                  (item as any).nlp_overall_confidence as number | null | undefined;

                return (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-3 py-2">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(item.id)}
                        onChange={() => toggleRow(item.id)}
                        title={`Select item ${item.id}`}
                        aria-label={`Select item ${item.id}`}
                      />
                    </td>
                    <td className="px-3 py-2 text-xs text-gray-500">{item.id}</td>
                    <td className="px-3 py-2">
                      <div className="max-w-xs truncate" title={item.item ?? ""}>
                        {item.item ?? <span className="text-gray-400">–</span>}
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      {item.amount != null ? item.amount.toFixed(2) : "–"}
                    </td>
                    <td className="px-3 py-2">
                      {item.date_str ?? <span className="text-gray-400">–</span>}
                    </td>
                    <td className="px-3 py-2">
                      <div
                        className="max-w-xs truncate text-xs text-gray-600"
                        title={item.source_file ?? ""}
                      >
                        {item.source_file ?? <span className="text-gray-400">–</span>}
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <span
                        className={
                          "inline-flex items-center rounded-full px-2 py-0.5 text-xs " +
                          iaConfidenceClass(conf)
                        }
                      >
                        {iaConfidenceLabel(conf)}
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
