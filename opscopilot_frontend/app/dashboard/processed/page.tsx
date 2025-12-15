import { apiGet } from "@/lib/api";

type ProcessedItem = {
  id: number;
  item: string | null;
  amount: number | null;
  date_str: string | null;
  source_file: string | null;
  created_at: string;
};

export default async function ProcessedListPage() {
  // Llama a tu FastAPI con Bearer
  const data = await apiGet<ProcessedItem[]>("/processed?limit=10");

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Últimos procesados</h2>
      <div className="overflow-auto border rounded-xl">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left p-2">ID</th>
              <th className="text-left p-2">Item</th>
              <th className="text-left p-2">Amount</th>
              <th className="text-left p-2">Date</th>
              <th className="text-left p-2">Source</th>
              <th className="text-left p-2">Created</th>
            </tr>
          </thead>
          <tbody>
            {data.map((r) => (
              <tr key={r.id} className="border-b">
                <td className="p-2">{r.id}</td>
                <td className="p-2">{r.item ?? "-"}</td>
                <td className="p-2">{r.amount ?? "-"}</td>
                <td className="p-2">{r.date_str ?? "-"}</td>
                <td className="p-2">{r.source_file ?? "-"}</td>
                <td className="p-2">{new Date(r.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
