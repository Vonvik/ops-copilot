"use client";

import Link from "next/link";
import { signOut, useSession } from "next-auth/react";

export default function Navbar() {
  const { data: session, status } = useSession();
  const role = session?.user.role ?? "USER";

  return (
    <header className="w-full border-b">
      <nav className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
        <Link href="/" className="font-semibold">OpsCopilot</Link>
        <Link href="/dashboard" className="text-sm">Dashboard</Link>
        {role === "ADMIN" && (
          <Link href="/admin" className="text-sm">Admin</Link>
        )}

        <div className="ml-auto flex items-center gap-3">
          {status === "authenticated" ? (
            <>
              <span className="text-sm leading-none">
                {session?.user?.email} ({role})
              </span>
              <button
                onClick={() => signOut({ callbackUrl: "/" })}
                className="rounded-xl border px-3 py-1 text-sm"
              >
                Logout
              </button>
            </>
          ) : (
            // 🔧 Arreglo 404: usa la ruta real del login
            <Link
              href="/auth/login"
              className="rounded-xl border px-3 py-1 text-sm"
            >
              Login
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
}
