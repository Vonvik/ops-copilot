// src/app/admin/page.tsx
import { redirect } from "next/navigation";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import RoleGateServer from "@/components/RoleGateServer";

export default async function AdminPage() {
  // 1) Sesión en servidor (seguridad "seria")
  const session = await getServerSession(authOptions);

  // Si no hay sesión (por si alguien esquiva el middleware)
  if (!session) {
    redirect("/auth/login");
  }

  // 2) Comprobar rol ADMIN a nivel de página
  const role = (session.user as any)?.role ?? "USER";

  if (role !== "ADMIN") {
    // Puedes cambiar "/dashboard" por lo que quieras
    redirect("/dashboard");
  }

  // 3) Contenido envuelto en tu RoleGateServer (por si quieres usar fallback/mensajes ahí)
  return (
    <RoleGateServer allow={["ADMIN"]}>
      <section className="space-y-4">
        <h1 className="text-2xl font-semibold">Panel Admin</h1>
        <p className="text-sm text-gray-600">
          Solo accesible para usuarios con rol <span className="font-semibold">ADMIN</span>.
        </p>

        <div className="rounded-xl border bg-white p-4 space-y-2">
          <p className="text-sm">
            Aquí más adelante podrás añadir:
          </p>
          <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
            <li>Gestión de usuarios</li>
            <li>Configuración global del sistema</li>
            <li>Logs / estado de tareas de OpsCopilot</li>
          </ul>
        </div>
      </section>
    </RoleGateServer>
  );
}
