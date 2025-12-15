// src/app/dashboard/nlp/history/page.tsx
"use client";

import { useEffect, useMemo, useState } from "react";
import { getNlpExtractions } from "@/lib/api";
import type { NLPHistoryItem } from "@/types/nlp";

function confidenceClass(conf?: number | null) {
  if (conf == null) return "bg-gray-100 text-gray-700";
  if (conf >= 0.8) return "bg-green-100 text-green-800";
  if (conf >= 0.4) return "bg-yellow-100 text-yellow-800";
  return "bg-red-100 text-red-800";
}

function confidenceLabel(conf?: number | null) {
  if (conf == null) return "-";
  return `${Math.round(conf * 100)}%`;
}

/**
 * El histórico (NLPHistoryItem) no incluye overall_confidence.
 * Derivamos una confianza "global" como media de las confianzas por campo
 * (ignorando nulls).
 */
function derivedOverallConfidence(it: NLPHistoryItem): number | null {
  const vals = [it.item_conf, it.amount_conf, it.date_conf].filter(
    (v): v is number => typeof v === "number"
  );
  if (vals.length === 0) return null;
  const sum = vals.reduce((a, b) => a + b, 0);
  return sum / vals.length;
}

export default function NlpHistoryPage() {
  const [items, setItems] = useState<NLPHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // filtros
  const [textFilter, setTextFilter] = useState("");
  const [minConf, setMinConf] = useState<number | "">("");
  const [onlyLowConf, setOnlyLowConf] = useState(false);

  async function loadHistory() {
    try {
      setLoading(true);
      setError(null);
      // cargamos 100 y filtramos aquí
      const data = await getNlpExtractions(100);
      setItems(data);
    } catch (err) {
      console.error(err);
      setError("Error cargando histórico de extracciones IA.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadHistory();
  }, []);

  const filteredItems = useMemo(() => {
    return items.filter((it) => {
      const text = textFilter.trim().toLowerCase();
      if (text) {
        const haystack = [it.raw_text ?? "", it.item ?? "", it.date_str ?? ""]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(text)) return false;
      }

      const globalConf = derivedOverallConfidence(it);

      if (minConf !== "") {
        if (globalConf == null || globalConf < minConf) return false;
      }

      if (onlyLowConf) {
        // mostramos solo las que están por debajo de 0.4 (o sin confianza)
        if (globalConf == null || globalConf >= 0.4) return false;
      }

      return true;
    });
  }, [items, textFilter, minConf, onlyLowConf]);

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-semibold">Histórico IA (NLP)</h1>
          <p className="text-sm text-gray-600">
            Registro de extracciones IA: texto original, campos detectados y
            niveles de confianza. Útil para ver dónde acierta y dónde falla.
          </p>
        </div>
        <button
          onClick={() => void loadHistory()}
          disabled={loading}
          className="px-3 py-1 rounded-md border text-sm hover:bg-gray-50 disabled:opacity-50"
        >
          Refrescar
        </button>
      </div>

      {/* Filtros */}
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div className="flex flex-col gap-2 md:flex-row md:items-end">
          <div className="space-y-1">
            <label className="block text-sm font-medium">Buscar</label>
            <input
              type="text"
              value={textFilter}
              onChange={(e) => setTextFilter(e.target.value)}
              placeholder="Texto, concepto, fecha..."
              className="w-full rounded-md border px-3 py-2 text-sm md:w-72"
            />
          </div>

          <div className="space-y-1 md:ml-4">
            <label className="block text-sm font-medium">
              Confianza global mínima (%)
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

        <div className="flex items-center gap-2">
          <input
            id="onlyLow"
            type="checkbox"
            checked={onlyLowConf}
            onChange={(e) => setOnlyLowConf(e.target.checked)}
          />
          <label htmlFor="onlyLow" className="text-sm text-gray-700">
            Mostrar solo casos de baja confianza (&lt; 40%)
          </label>
        </div>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}

      {loading && !items.length ? (
        <p className="text-sm text-gray-500">Cargando histórico…</p>
      ) : null}

      {!loading && items.length === 0 ? (
        <p className="text-sm text-gray-500">
          Aún no hay extracciones IA registradas.
        </p>
      ) : null}

      {items.length > 0 && (
        <div className="overflow-x-auto border rounded-lg">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  ID
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Texto original
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Item
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Importe
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Fecha
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Conf. item
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Conf. importe
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Conf. fecha
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Conf. global
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map((it) => {
                const g = derivedOverallConfidence(it);
                return (
                  <tr key={it.id} className="border-t hover:bg-gray-50">
                    <td className="px-3 py-2 text-xs text-gray-500">{it.id}</td>
                    <td className="px-3 py-2 max-w-xs">
                      <div
                        className="truncate text-xs text-gray-700"
                        title={it.raw_text ?? ""}
                      >
                        {it.raw_text ?? <span className="text-gray-400">–</span>}
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      {it.item ?? <span className="text-gray-400">–</span>}
                    </td>
                    <td className="px-3 py-2">
                      {it.amount != null ? it.amount.toFixed(2) : "–"}
                    </td>
                    <td className="px-3 py-2">
                      {it.date_str ?? <span className="text-gray-400">–</span>}
                    </td>
                    <td className="px-3 py-2">
                      <span
                        className={
                          "inline-flex items-center rounded-full px-2 py-0.5 text-xs " +
                          confidenceClass(it.item_conf)
                        }
                      >
                        {confidenceLabel(it.item_conf)}
                      </span>
                    </td>
                    <td className="px-3 py-2">
                      <span
                        className={
                          "inline-flex items-center rounded-full px-2 py-0.5 text-xs " +
                          confidenceClass(it.amount_conf)
                        }
                      >
                        {confidenceLabel(it.amount_conf)}
                      </span>
                    </td>
                    <td className="px-3 py-2">
                      <span
                        className={
                          "inline-flex items-center rounded-full px-2 py-0.5 text-xs " +
                          confidenceClass(it.date_conf)
                        }
                      >
                        {confidenceLabel(it.date_conf)}
                      </span>
                    </td>
                    <td className="px-3 py-2">
                      <span
                        className={
                          "inline-flex items-center rounded-full px-2 py-0.5 text-xs " +
                          confidenceClass(g)
                        }
                      >
                        {confidenceLabel(g)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
