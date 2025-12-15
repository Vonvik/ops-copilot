"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useSearchParams, useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const searchParams = useSearchParams();
  const router = useRouter();
  const callbackUrl = searchParams.get("callbackUrl") || "/dashboard";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    setLoading(true);

    const result = await signIn("credentials", {
      redirect: false,
      email,
      password: pass,
      callbackUrl,
    });

    setLoading(false);

    if (result?.error) {
      setMsg("Credenciales inválidas");
      return;
    }

    // Login OK → redirigimos
    router.push(callbackUrl);
  }

  return (
    <section className="max-w-md space-y-6">
      <h1 className="text-2xl font-semibold">Login</h1>
      <p className="text-sm text-gray-500">
        Accede con tu usuario para ver el dashboard.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4 rounded border bg-white p-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium">Email</label>
          <input
            type="email"
            className="w-full rounded border px-3 py-2 outline-none focus:ring"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin@test.com"
            required
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">Contraseña</label>
          <input
            type="password"
            className="w-full rounded border px-3 py-2 outline-none focus:ring"
            value={pass}
            onChange={(e) => setPass(e.target.value)}
            placeholder="••••••••"
            required
            minLength={6}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="rounded bg-black text-white px-4 py-2 disabled:opacity-50"
        >
          {loading ? "Entrando..." : "Entrar"}
        </button>
        <button
          type="button"
          onClick={() => signIn("google", { callbackUrl: "/dashboard" })}
          className="w-full rounded border px-4 py-2 text-sm"
        >
          Entrar con Google
        </button>

        {msg && <div className="text-sm text-red-600">{msg}</div>}
      </form>
    </section>
  );
}
