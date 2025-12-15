// src/components/RequireRole.tsx
"use client";

import { ReactNode } from "react";
import { useSession } from "next-auth/react";

interface Props {
  role?: "ADMIN" | "USER";
  children: ReactNode;
  fallback?: ReactNode;
}

export function RequireRole({ role = "USER", children, fallback }: Props) {
  const { data: session, status } = useSession();

  if (status === "loading") {
    return <p className="text-sm text-gray-500">Comprobando permisos...</p>;
  }

  if (!session) {
    return (
      <p className="text-sm text-red-600">
        Debes iniciar sesión para ver este contenido.
      </p>
    );
  }

  const userRole = (session.user as any)?.role ?? "USER";

  if (role === "ADMIN" && userRole !== "ADMIN") {
    return (
      fallback ?? (
        <p className="text-sm text-red-600">
          No tienes permisos para ver este contenido.
        </p>
      )
    );
  }

  return <>{children}</>;
}
