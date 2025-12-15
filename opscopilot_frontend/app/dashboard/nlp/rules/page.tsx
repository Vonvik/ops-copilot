"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  getNlpRules,
  createNlpRule,
  updateNlpRule,
  deleteNlpRule,
  type NlpRulePayload,
} from "@/lib/api";
import type { NLPConfidenceRule, NLPRuleAction } from "@/types/nlp";

const ACTIONS: NLPRuleAction[] = [
  "AUTO_ACCEPT",
  "REVIEW",
  "IGNORE_OR_SUGGEST",
];

export default function NlpRulesPage() {
  const [rules, setRules] = useState<NLPConfidenceRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Formulario creación
  const [minConf, setMinConf] = useState("0.0");
  const [maxConf, setMaxConf] = useState("1.0");
  const [action, setAction] = useState<NLPRuleAction>("REVIEW");
  const [isActive, setIsActive] = useState(true);

  async function loadRules() {
    try {
      setLoading(true);
      setError(null);
      const data = await getNlpRules();
      setRules(data);
    } catch (err: any) {
      console.error(err);
      setError("Error cargando reglas NLP");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadRules();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      setSaving(true);
      setError(null);

      const min = parseFloat(minConf.replace(",", "."));
      const max = parseFloat(maxConf.replace(",", "."));
      if (Number.isNaN(min) || Number.isNaN(max)) {
        setError("min_confidence y max_confidence deben ser números");
        return;
      }

      const payload: NlpRulePayload = {
        min_confidence: min,
        max_confidence: max,
        action,
        is_active: isActive,
      };

      const created = await createNlpRule(payload);
      setRules((prev) =>
        [...prev, created].sort(
          (a, b) => a.min_confidence - b.min_confidence
        )
      );

      // limpiar form
      setMinConf("0.0");
      setMaxConf("1.0");
      setAction("REVIEW");
      setIsActive(true);
    } catch (err: any) {
      console.error(err);
      setError("No se pudo crear la regla");
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleActive(rule: NLPConfidenceRule) {
    try {
      setError(null);
      const updated = await updateNlpRule(rule.id, {
        is_active: !rule.is_active,
      });
      setRules((prev) =>
        prev.map((r) => (r.id === rule.id ? updated : r))
      );
    } catch (err: any) {
      console.error(err);
      setError("No se pudo actualizar la regla");
    }
  }

  async function handleDelete(ruleId: number) {
    if (!confirm("¿Seguro que quieres eliminar esta regla?")) return;
    try {
      setError(null);
      await deleteNlpRule(ruleId);
      setRules((prev) => prev.filter((r) => r.id !== ruleId));
    } catch (err: any) {
      console.error(err);
      setError("No se pudo eliminar la regla");
    }
  }

  return (
    <section className="space-y-6 p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">
            Reglas de confianza de la IA (NLP)
          </h1>
          <p className="text-sm text-gray-600">
            Aquí configuras qué hace el sistema según la confianza global de la
            IA: auto-aprobar, enviar a revisión o sólo sugerir.
          </p>
        </div>
        <Link
          href="/dashboard/nlp"
          className="rounded-md border px-3 py-1.5 text-sm hover:bg-gray-50"
        >
          Ver monitor IA
        </Link>
      </div>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}

      {/* Formulario de creación */}
      <div className="rounded border bg-white p-4 space-y-3">
        <h2 className="text-sm font-semibold">Nueva regla</h2>
        <form onSubmit={handleCreate} className="grid gap-3 md:grid-cols-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium">
              min_confidence
            </label>
            <input
              type="number"
              step="0.01"
              min={0}
              max={1}
              value={minConf}
              onChange={(e) => setMinConf(e.target.value)}
              placeholder="0.0"
              className="w-full rounded border px-2 py-1 text-sm"
            />
          <div className="space-y-1">
            <label className="block text-xs font-medium">
              max_confidence
            </label>
            <input
              type="number"
              step="0.01"
              min={0}
              max={1}
              value={maxConf}
              onChange={(e) => setMaxConf(e.target.value)}
              placeholder="1.0"
              className="w-full rounded border px-2 py-1 text-sm"
            />
          </div>
          </div>
          <div className="space-y-1">
            <label htmlFor="action-select" className="block text-xs font-medium">Acción</label>
            <select
              id="action-select"
              value={action}
              onChange={(e) => setAction(e.target.value as NLPRuleAction)}
              className="w-full rounded border px-2 py-1 text-sm"
            >
              {ACTIONS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium">Activa</label>
            <div className="flex items-center gap-2">
              <input
                id="is_active"
                type="checkbox"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
              />
              <label htmlFor="is_active" className="text-xs">
                Regla activa
              </label>
            </div>
          </div>
          <div className="md:col-span-4 flex justify-end pt-1">
            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? "Guardando..." : "Crear regla"}
            </button>
          </div>
        </form>
      </div>

      {/* Tabla de reglas */}
      <div className="rounded border bg-white overflow-x-auto">
        {loading ? (
          <p className="px-3 py-2 text-sm text-gray-500">Cargando reglas…</p>
        ) : rules.length === 0 ? (
          <p className="px-3 py-2 text-sm text-gray-500">
            No hay reglas definidas todavía.
          </p>
        ) : (
          <table className="min-w-full text-xs md:text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-2 py-2 text-left">ID</th>
                <th className="px-2 py-2 text-left">min_conf</th>
                <th className="px-2 py-2 text-left">max_conf</th>
                <th className="px-2 py-2 text-left">Acción</th>
                <th className="px-2 py-2 text-left">Activa</th>
                <th className="px-2 py-2 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {rules.map((r) => (
                <tr key={r.id} className="border-t">
                  <td className="px-2 py-1">{r.id}</td>
                  <td className="px-2 py-1">
                    {r.min_confidence.toFixed(2)}
                  </td>
                  <td className="px-2 py-1">
                    {r.max_confidence.toFixed(2)}
                  </td>
                  <td className="px-2 py-1">{r.action}</td>
                  <td className="px-2 py-1">
                    <button
                      type="button"
                      onClick={() => void handleToggleActive(r)}
                      className={
                        "inline-flex items-center rounded-full px-2 py-0.5 text-xs " +
                        (r.is_active
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-600")
                      }
                    >
                      {r.is_active ? "Activa" : "Inactiva"}
                    </button>
                  </td>
                  <td className="px-2 py-1 text-right">
                    <button
                      type="button"
                      onClick={() => void handleDelete(r.id)}
                      className="inline-flex items-center rounded-md border border-red-500 px-2 py-0.5 text-xs text-red-600 hover:bg-red-50"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
