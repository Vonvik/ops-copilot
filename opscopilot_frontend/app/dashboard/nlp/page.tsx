// src/app/dashboard/nlp/page.tsx
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import Link from "next/link";

import { getNlpExtractions } from "@/lib/api";
import type { NLPHistoryItem } from "@/types/nlp";

function avg(nums: number[]): number {
  if (!nums.length) return 0;
  const sum = nums.reduce((acc, v) => acc + v, 0);
  return sum / nums.length;
}

function toPct(n: number | null | undefined): string {
  if (n == null) return "-";
  return `${Math.round(n * 100)}%`;
}

export default async function NlpMonitorPage() {
  const session = await getServerSession(authOptions);

  if (!session) {
    return (
      <div className="space-y-2">
        <h1 className="text-xl font-semibold">Monitor IA (NLP)</h1>
        <p className="text-sm text-gray-600">No autenticado.</p>
        <Link href="/auth/login" className="text-sm underline">
          Ir a login
        </Link>
      </div>
    );
  }

  const extractions: NLPHistoryItem[] = await getNlpExtractions(50);

  const itemConfs = extractions
    .map((e) => e.item_conf)
    .filter((v): v is number => v != null);
  const amountConfs = extractions
    .map((e) => e.amount_conf)
    .filter((v): v is number => v != null);
  const dateConfs = extractions
    .map((e) => e.date_conf)
    .filter((v): v is number => v != null);

  const avgItem = avg(itemConfs);
  const avgAmount = avg(amountConfs);
  const avgDate = avg(dateConfs);

  return (
    <section className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">Monitor de IA (extracciones NLP)</h1>
          <p className="text-sm text-gray-600">
            Aquí puedes ver las últimas extracciones que ha hecho la IA y cómo de
            segura estaba en cada campo.
          </p>
        </div>
        <Link
          href="/dashboard"
          className="rounded-md border px-3 py-1.5 text-sm hover:bg-gray-50"
        >
          Volver al dashboard
        </Link>
      </div>

      {/* KPIs rápidos */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-lg border bg-gray-50 p-3">
          <p className="text-xs text-gray-500">Extracciones analizadas</p>
          <p className="text-2xl font-semibold">{extractions.length}</p>
        </div>
        <div className="rounded-lg border bg-gray-50 p-3">
          <p className="text-xs text-gray-500">Confianza media – Concepto</p>
          <p className="text-2xl font-semibold">{toPct(avgItem)}</p>
        </div>
        <div className="rounded-lg border bg-gray-50 p-3">
          <p className="text-xs text-gray-500">Confianza media – Importe</p>
          <p className="text-2xl font-semibold">{toPct(avgAmount)}</p>
        </div>
        {/* Si quieres, podrías añadir Fecha como 4ª tarjeta */}
      </div>

      {/* Tabla de extracciones */}
      {extractions.length === 0 ? (
        <p className="text-sm text-gray-500">
          Aún no hay extracciones NLP guardadas en el histórico.
        </p>
      ) : (
        <div className="overflow-x-auto border rounded-lg">
          <table className="min-w-full text-xs md:text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-2 py-2 text-left">ID</th>
                <th className="px-2 py-2 text-left">Fecha</th>
                <th className="px-2 py-2 text-left">Texto bruto</th>
                <th className="px-2 py-2 text-left">Item</th>
                <th className="px-2 py-2 text-left">Importe</th>
                <th className="px-2 py-2 text-left">Fecha detectada</th>
                <th className="px-2 py-2 text-left">Conf. Item</th>
                <th className="px-2 py-2 text-left">Conf. Importe</th>
                <th className="px-2 py-2 text-left">Conf. Fecha</th>
              </tr>
            </thead>
            <tbody>
              {extractions.map((e) => (
                <tr key={e.id} className="border-t align-top">
                  <td className="px-2 py-1">{e.id}</td>
                  <td className="px-2 py-1">
                    {e.created_at
                      ? new Date(e.created_at).toLocaleString()
                      : "-"}
                  </td>
                  <td className="px-2 py-1 max-w-xs truncate" title={e.raw_text}>
                    {e.raw_text}
                  </td>
                  <td className="px-2 py-1">{e.item ?? "-"}</td>
                  <td className="px-2 py-1">
                    {e.amount != null ? e.amount.toFixed(2) : "-"}
                  </td>
                  <td className="px-2 py-1">{e.date_str ?? "-"}</td>
                  <td className="px-2 py-1">{toPct(e.item_conf)}</td>
                  <td className="px-2 py-1">{toPct(e.amount_conf)}</td>
                  <td className="px-2 py-1">{toPct(e.date_conf)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
