// components/processed/NewExpenseForm.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { extractNlp, createProcessed } from "@/lib/api";
import type { NLPExtraction } from "@/types/nlp";
import type { ProcessedItem } from "@/types/processed";

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

// 🔹 NUEVO: mensaje de ayuda según la confianza global
function globalConfidenceAdvice(conf?: number | null) {
  if (conf == null) return null;
  if (conf >= 0.8) {
    return "La IA está bastante segura. Solo haz una última revisión rápida antes de guardar.";
  }
  if (conf >= 0.4) {
    return "Confianza media: revisa bien concepto, importe y fecha antes de confirmar.";
  }
  return "Confianza baja: tómalo solo como sugerencia y ajusta los campos manualmente.";
}

export default function NewExpenseForm() {
  const router = useRouter();

  const [rawText, setRawText] = useState("");
  const [item, setItem] = useState<string | "">("");
  const [amount, setAmount] = useState<string>("");
  const [dateStr, setDateStr] = useState<string>("");
  const [sourceFile, setSourceFile] = useState<string>("manual");

  const [nlp, setNlp] = useState<NLPExtraction | null>(null);
  const [saving, setSaving] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleExtract() {
    if (!rawText.trim()) {
      setError("Introduce alguna línea de texto para analizar.");
      return;
    }
    try {
      setExtracting(true);
      setError(null);
      setMessage(null);
      const res = await extractNlp(rawText.trim());
      setNlp(res);

      // Autorrellenar campos si vienen
      if (res.item != null) setItem(res.item);
      if (res.amount != null) setAmount(String(res.amount));
      if (res.date_str != null) setDateStr(res.date_str);
    } catch (err: any) {
      console.error(err);
      setError("Error llamando al servicio de IA.");
    } finally {
      setExtracting(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    // Normalizamos amount a número o null
    const parsedAmount =
      amount.trim() === "" ? null : Number.parseFloat(amount.replace(",", "."));

    if (parsedAmount !== null && Number.isNaN(parsedAmount as number)) {
      setError("La cantidad no es válida.");
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setMessage(null);

      const body = {
        item: item.trim() === "" ? null : item.trim(),
        amount: parsedAmount,
        date_str: dateStr || null,
        source_file: sourceFile || "manual",
        nlp_overall_confidence: nlp?.overall_confidence ?? null,
      };

      const saved: ProcessedItem = await createProcessed(body);

      setMessage(`Gasto guardado (ID ${saved.id}).`);

      // 🔄 Forzar que el dashboard (Server Component) se vuelva a renderizar
      router.refresh();

      // Opcional: limpiar formulario
      // setRawText("");
      // setItem("");
      // setAmount("");
      // setDateStr("");
    } catch (err: any) {
      console.error(err);
      setError("No se pudo guardar el gasto.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4 rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Nuevo gasto (asistido por IA)</h2>
      <p className="text-sm text-gray-600">
        Pega una línea de tu extracto (banco, tarjeta, ticket). La IA intentará
        extraer concepto, importe y fecha. Luego puedes corregirlo antes de guardar.
      </p>

      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}
      {message && (
        <div className="rounded-md bg-green-50 border border-green-200 px-3 py-2 text-sm text-green-800">
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Texto libre para NLP */}
        <div className="space-y-1">
          <label className="block text-sm font-medium">
            Línea de extracto / ticket
          </label>
          <textarea
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            rows={3}
            className="w-full rounded-md border px-3 py-2 text-sm"
            placeholder="Ejemplo: COMPRA AMAZON 25,60 EUR 12/11/2025"
          />
          <button
            type="button"
            onClick={() => void handleExtract()}
            disabled={extracting}
            className="mt-1 inline-flex items-center rounded-md border px-3 py-1 text-sm hover:bg-gray-50 disabled:opacity-50"
          >
            {extracting ? "Analizando..." : "Extraer con IA"}
          </button>
        </div>

        {/* Campos estructurados */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="space-y-1">
            <label className="block text-sm font-medium">
              Concepto
              {nlp && (
                <span
                  className={
                    "ml-2 inline-flex items-center rounded-full px-2 py-0.5 text-xs " +
                    confidenceClass(nlp.item_conf)
                  }
                >
                  IA: {confidenceLabel(nlp.item_conf)}
                </span>
              )}
            </label>
            <input
              type="text"
              value={item}
              onChange={(e) => setItem(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm"
              placeholder="Ej. AMAZON"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium">
              Importe
              {nlp && (
                <span
                  className={
                    "ml-2 inline-flex items-center rounded-full px-2 py-0.5 text-xs " +
                    confidenceClass(nlp.amount_conf)
                  }
                >
                  IA: {confidenceLabel(nlp.amount_conf)}
                </span>
              )}
            </label>
            <input
              type="text"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm"
              placeholder="Ej. 25.60"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium">
              Fecha
              {nlp && (
                <span
                  className={
                    "ml-2 inline-flex items-center rounded-full px-2 py-0.5 text-xs " +
                    confidenceClass(nlp.date_conf)
                  }
                >
                  IA: {confidenceLabel(nlp.date_conf)}
                </span>
              )}
            </label>
            <input
              type="date"
              value={dateStr}
              onChange={(e) => setDateStr(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm"
              placeholder="Ej. 2025-11-12"
              title="Fecha del gasto"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium">Fuente</label>
            <input
              type="text"
              value={sourceFile}
              onChange={(e) => setSourceFile(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm"
              placeholder="Ej. banco_noviembre.csv"
            />
          </div>
        </div>

        {/* Confianza global + consejo IA */}
        {nlp && (
          <div className="text-sm text-gray-700">
            Confianza global IA:{" "}
            <span
              className={
                "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium " +
                confidenceClass(nlp.overall_confidence)
              }
            >
              {confidenceLabel(nlp.overall_confidence)}
            </span>
            <span className="ml-2 text-xs text-gray-500">
              (&lt; 40%: rojo, 40–80%: amarillo, &gt;= 80%: verde)
            </span>

            {/* 🔹 NUEVO: mensaje según el nivel de confianza */}
            {globalConfidenceAdvice(nlp.overall_confidence) && (
              <p className="mt-1 text-xs text-gray-600">
                {globalConfidenceAdvice(nlp.overall_confidence)}
              </p>
            )}
          </div>
        )}

        <div className="pt-2">
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Guardando..." : "Guardar gasto"}
          </button>
        </div>
      </form>
    </div>
  );
}
