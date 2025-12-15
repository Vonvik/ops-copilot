import Link from "next/link";

export default function Sidebar() {
  return (
    <aside className="w-60 border-r h-full bg-white">
      <div className="p-4 font-semibold">Menú</div>
      <ul className="space-y-1 px-2">
        <li><Link className="block rounded px-3 py-2 hover:bg-gray-100" href="/dashboard">Dashboard</Link></li>
        <li><Link className="block rounded px-3 py-2 hover:bg-gray-100" href="/login">Login</Link></li>
        <li><Link href="/dashboard/approvals" className="block rounded px-3 py-2 text-sm hover:bg-gray-100">Aprobaciones</Link></li>
      </ul>
    </aside>
  );
}
