// src/app/dashboard/approvals/page.tsx
"use client";

import { useEffect, useMemo, useState } from "react";
import {
  getPendingProcessed,
  approveProcessed,
  rejectProcessed,
} from "@/lib/api";
import type { ProcessedItem } from "@/types/processed";

function confidenceColor(conf?: number | null) {
  if (conf == null) return "bg-gray-200 text-gray-800";
  if (conf >= 0.8) return "bg-green-100 text-green-800";
  if (conf >= 0.4) return "bg-yellow-100 text-yellow-800";
  return "bg-red-100 text-red-800";
}

function formatConfidence(conf?: number | null) {
  if (conf == null) return "-";
  return `${Math.round(conf * 100)}%`;
}

// 🔹 Helpers para el estado de revisión
type Status = ProcessedItem["review_status"];

function statusColor(status: Status) {
  switch (status) {
    case "approved":
      return "bg-green-100 text-green-800";
    case "rejected":
      return "bg-red-100 text-red-800";
    case "pending":
    default:
      return "bg-yellow-100 text-yellow-800";
  }
}

function statusLabel(status: Status) {
  switch (status) {
    case "approved":
      return "Aprobado";
    case "rejected":
      return "Rechazado";
    case "pending":
    default:
      return "Pendiente";
  }
}

export default function ApprovalsPage() {
  const [items, setItems] = useState<ProcessedItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionId, setActionId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 🔹 NUEVO: filtros y selección
  const [textFilter, setTextFilter] = useState("");
  const [minConf, setMinConf] = useState<number | "">("");
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [batchLoading, setBatchLoading] = useState<"approve" | "reject" | null>(
    null,
  );

  async function loadPending() {
    try {
      setLoading(true);
      setError(null);
      const data = await getPendingProcessed();
      setItems(data);
      setSelectedIds([]);
    } catch (err: any) {
      console.error(err);
      setError("Error cargando pendientes de revisión");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadPending();
  }, []);

  async function handleApprove(id: number) {
    try {
      setActionId(id);
      setError(null);
      await approveProcessed(id);
      // quitamos el elemento de la lista
      setItems((prev) => prev.filter((it) => it.id !== id));
      setSelectedIds((prev) => prev.filter((x) => x !== id));
    } catch (err: any) {
      console.error(err);
      setError("No se pudo aprobar el registro");
    } finally {
      setActionId(null);
    }
  }

  async function handleReject(id: number) {
    try {
      setActionId(id);
      setError(null);
      await rejectProcessed(id);
      setItems((prev) => prev.filter((it) => it.id !== id));
      setSelectedIds((prev) => prev.filter((x) => x !== id));
    } catch (err: any) {
      console.error(err);
      setError("No se pudo rechazar el registro");
    } finally {
      setActionId(null);
    }
  }

  // 🔹 Filtro en memoria
  const filteredItems = useMemo(() => {
    return items.filter((it) => {
      const text = textFilter.trim().toLowerCase();
      if (text) {
        const haystack = [
          it.item ?? "",
          it.source_file ?? "",
          it.date_str ?? "",
        ]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(text)) {
          return false;
        }
      }

      if (minConf !== "") {
        const conf = it.nlp_overall_confidence;
        if (conf == null || conf < minConf) {
          return false;
        }
      }

      return true;
    });
  }, [items, textFilter, minConf]);

  // 🔹 Selección múltiple
  const allVisibleSelected =
    filteredItems.length > 0 &&
    filteredItems.every((it) => selectedIds.includes(it.id));

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
      setBatchLoading(kind);
      setError(null);

      const ids = [...selectedIds];

      for (const id of ids) {
        if (kind === "approve") {
          await approveProcessed(id);
        } else {
          await rejectProcessed(id);
        }
      }

      setItems((prev) => prev.filter((it) => !ids.includes(it.id)));
      setSelectedIds((prev) => prev.filter((id) => !ids.includes(id)));
    } catch (err) {
      console.error(err);
      setError(
        "Error al procesar la acción masiva. Revisa la consola o inténtalo de nuevo.",
      );
    } finally {
      setBatchLoading(null);
    }
  }

  return (
    <div className="space-y-4">
      {/* Cabecera + contador + refresco */}
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-semibold">
            Revisión de gastos (cola humana)
          </h1>
          <p className="text-sm text-gray-600">
            Aquí ves los registros que la IA marcó como “necesitan revisión”.
          </p>
          {!loading && (
            <p className="mt-1 text-xs text-gray-500">
              Pendientes actualmente:{" "}
              <span className="font-semibold">{items.length}</span>
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => void loadPending()}
            disabled={loading}
            className="px-3 py-1 rounded-md border text-sm hover:bg-gray-50 disabled:opacity-50"
          >
            Refrescar
          </button>
        </div>
      </div>

      {/* Filtros + acciones masivas */}
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
                    // guardamos 0–1 internamente
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
            disabled={selectedIds.length === 0 || batchLoading !== null}
            onClick={() => void handleBatchAction("approve")}
            className="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
          >
            {batchLoading === "approve"
              ? "Aprobando..."
              : `Aprobar seleccionados (${selectedIds.length})`}
          </button>
          <button
            type="button"
            disabled={selectedIds.length === 0 || batchLoading !== null}
            onClick={() => void handleBatchAction("reject")}
            className="inline-flex items-center rounded-md bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
          >
            {batchLoading === "reject"
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

      {loading && !items.length ? (
        <p className="text-sm text-gray-500">Cargando pendientes…</p>
      ) : null}

      {!loading && items.length === 0 ? (
        <p className="text-sm text-gray-500">
          No hay registros pendientes de revisión. 🎉
        </p>
      ) : null}

      {items.length > 0 && (
        <div className="overflow-x-auto border rounded-lg">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left">
                  <input
                    type="checkbox"
                    title="Seleccionar todos los registros visibles"
                    checked={allVisibleSelected}
                    onChange={toggleSelectAllVisible}
                  />
                </th>
                <th className="px-3 py-2 text-left">ID</th>
                <th className="px-3 py-2 text-left">Item</th>
                <th className="px-3 py-2 text-left">Cantidad</th>
                <th className="px-3 py-2 text-left">Fecha</th>
                <th className="px-3 py-2 text-left">Archivo</th>
                <th className="px-3 py-2 text-left">Confianza IA</th>
                <th className="px-3 py-2 text-left">Estado</th>
                <th className="px-3 py-2 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map((it) => (
                <tr key={it.id} className="border-t hover:bg-gray-50">
                  <td className="px-3 py-2">
                    <input
                      type="checkbox"
                      title="Seleccionar registro"
                      checked={selectedIds.includes(it.id)}
                      onChange={() => toggleRow(it.id)}
                    />
                  </td>
                  <td className="px-3 py-2">{it.id}</td>
                  <td className="px-3 py-2">{it.item}</td>
                  <td className="px-3 py-2">
                    {it.amount != null ? it.amount.toFixed(2) : "-"}
                  </td>
                  <td className="px-3 py-2">{it.date_str ?? "-"}</td>
                  <td className="px-3 py-2">{it.source_file ?? "-"}</td>
                  <td className="px-3 py-2">
                    <span
                      className={
                        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium " +
                        confidenceColor(it.nlp_overall_confidence)
                      }
                    >
                      {formatConfidence(it.nlp_overall_confidence)}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <span
                      className={
                        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium " +
                        statusColor(it.review_status)
                      }
                    >
                      {statusLabel(it.review_status)}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right space-x-2">
                    <button
                      onClick={() => void handleApprove(it.id)}
                      disabled={actionId === it.id || batchLoading !== null}
                      className="px-2 py-1 rounded-md border border-green-600 text-green-700 text-xs hover:bg-green-50 disabled:opacity-50"
                    >
                      Aprobar
                    </button>
                    <button
                      onClick={() => void handleReject(it.id)}
                      disabled={actionId === it.id || batchLoading !== null}
                      className="px-2 py-1 rounded-md border border-red-600 text-red-700 text-xs hover:bg-red-50 disabled:opacity-50"
                    >
                      Rechazar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
