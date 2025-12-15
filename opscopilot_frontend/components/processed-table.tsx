"use client";

import { useEffect, useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import { toast } from "sonner";

import { DataTable } from "@/components/data-table";
import { Skeleton } from "@/components/ui/skeleton";
import { apiGet } from "@/lib/api";
import { Processed, ProcessedListSchema } from "@/types/processed";

/* ================== Columnas ================== */
const columns: ColumnDef<Processed>[] = [
  { accessorKey: "id", header: "ID" },
  { accessorKey: "item", header: "Concepto" },
  { accessorKey: "amount", header: "Importe" },
  { accessorKey: "date_str", header: "Fecha" },
  { accessorKey: "source_file", header: "Origen" },
  {
    accessorKey: "created_at",
    header: "Creado",
    cell: ({ getValue }) => {
      const v = getValue<string>();
      if (!v) return "—";
      const d = new Date(v);
      return isNaN(d.getTime()) ? v : d.toLocaleString();
    },
  },
];

type Props = { limit?: number };

/* ================== Componente ================== */
export default function ProcessedTable({ limit = 20 }: Props) {
  const [data, setData] = useState<Processed[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      setLoading(true);
      // NO pongas /api/v1 aquí si NEXT_PUBLIC_API_URL ya lo incluye
      const raw = await apiGet<unknown>(`/processed?limit=${limit}`);
      const parsed = ProcessedListSchema.safeParse(raw);

      if (!parsed.success) {
        console.error(parsed.error);
        toast.error("Respuesta inválida de la API");
        return;
      }

      // Normalizamos por si el backend devuelve null/undefined en algún campo
      const normalized: Processed[] = parsed.data.map((item) => ({
        id: item.id,
        item: item.item ?? null,
        amount: item.amount ?? null,
        date_str: item.date_str ?? null,
        source_file: item.source_file ?? null,
        created_at:
          item.created_at ??
          item.date_str /* fallback útil */ ??
          new Date().toISOString(),
      }));

      setData(normalized);
    } catch (err: any) {
      console.error(err);
      // Si api.ts lanza ApiError(payload), intenta mostrar detail
      const detail =
        err?.payload ||
        err?.response?.data?.detail ||
        err?.message ||
        "Error cargando datos";
      toast.error(typeof detail === "string" ? detail : "Error cargando datos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [limit]);

  if (loading) return <Skeleton className="h-48 w-full" />;

  return (
    <DataTable
      columns={columns}
      data={data}
      caption={`Últimos ${limit} registros`}
      loading={loading}
    />
  );
}
