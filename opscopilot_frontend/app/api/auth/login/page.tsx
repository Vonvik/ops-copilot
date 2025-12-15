"use client";

import { signIn } from "next-auth/react";
import { useState } from "react";
import Link from "next/link";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    // Redirige a /dashboard si el login es correcto
    await signIn("credentials", {
      email,
      password,
      redirect: true,
      callbackUrl: "/dashboard",
    });
    setLoading(false);
  }

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-6">
      <div className="max-w-md w-full rounded-2xl shadow p-6 space-y-4" role="form" aria-labelledby="login-title">
        <h1 id="login-title" className="text-2xl font-semibold">Iniciar sesión</h1>

        {err && (
          <p className="text-sm text-red-600" role="alert" aria-live="assertive">
            {err}
          </p>
        )}

        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          {/* Email */}
          <div className="space-y-1">
            <label htmlFor="email" className="text-sm">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              inputMode="email"
              className="w-full border rounded-xl p-2"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              aria-required="true"
              autoComplete="email"
              placeholder="tucorreo@dominio.com"
            />
          </div>

          {/* Password */}
          <div className="space-y-1">
            <label htmlFor="password" className="text-sm">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              className="w-full border rounded-xl p-2"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              aria-required="true"
              autoComplete="current-password"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl p-2 border"
            aria-label="Entrar con email y contraseña"
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <div className="pt-2">
          <button
            onClick={() => signIn("google", { callbackUrl: "/dashboard" })}
            className="w-full rounded-xl p-2 border"
            aria-label="Continuar con Google"
            type="button"
          >
            Continuar con Google
          </button>
        </div>

        <p className="text-xs text-center text-gray-500">
          ¿No tienes cuenta?{" "}
          <Link href="#" className="underline">
            Contacta con admin
          </Link>
        </p>
      </div>
    </div>
  );
}
