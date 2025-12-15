// src/lib/auth.ts
import type { NextAuthOptions } from "next-auth";
import Credentials from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";

function hasGoogleEnv() {
  return !!process.env.GOOGLE_CLIENT_ID && !!process.env.GOOGLE_CLIENT_SECRET;
}

export const authOptions: NextAuthOptions = {
  session: { strategy: "jwt" },
  pages: { signIn: "/auth/login" },

  providers: [
    // ------------------------------------------------------------------
    // CREDENTIALS PROVIDER (DEV)
    // Aquí hacemos login en memoria, sin tocar FastAPI.
    // admin@test.com / Admin123! -> ADMIN
    // ------------------------------------------------------------------
    Credentials({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const email = credentials?.email;
        const password = credentials?.password;

        // ⚠️ DEV ONLY: credenciales fijas
        if (email === "admin@test.com" && password === "Admin123!") {
          return {
            id: "1",
            email,
            name: "Admin",
            role: "ADMIN" as const,
            accessToken: "dev-dummy-token",
          };
        }

        // Aquí podrías añadir otros usuarios de prueba si quieres:
        //
        // if (email === "user@test.com" && password === "User123!") {
        //   return {
        //     id: "2",
        //     email,
        //     name: "User",
        //     role: "USER" as const,
        //     accessToken: "dev-dummy-token-user",
        //   };
        // }

        // Si no coincide ninguna credencial de dev → error de login
        return null;
      },
    }),

    // ------------------------------------------------------------------
    // GOOGLE PROVIDER (lo dejamos listo por si lo activas)
    // ------------------------------------------------------------------
    ...(hasGoogleEnv()
      ? [
          GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID as string,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
            allowDangerousEmailAccountLinking: true,
          }),
        ]
      : []),
  ],

  callbacks: {
    // Si en el futuro vuelves a usar Google + sync_oauth, puedes reactivar aquí
    async signIn({ user, account }) {
      // Mantengo el patrón, pero en dev no hace nada si no hay API_BASE_URL
      if (account?.provider === "google" && user?.email) {
        const apiBase =
          process.env.INTERNAL_API_URL ?? process.env.API_BASE_URL;
        if (apiBase) {
          try {
            const res = await fetch(`${apiBase}/auth/sync_oauth`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ email: user.email }),
            });
            if (res.ok) {
              const info = await res.json();
              (user as any).role = (info.role ?? "USER") as "ADMIN" | "USER";
              (user as any).accessToken = info.access_token ?? undefined;
            } else {
              (user as any).role = "USER";
            }
          } catch {
            (user as any).role = "USER";
          }
        }
      }
      return true;
    },

    async jwt({ token, user }) {
      if (user) {
        token.role = (user as any).role ?? token.role ?? "USER";
        token.accessToken = (user as any).accessToken ?? token.accessToken;
      }
      return token;
    },

    async session({ session, token }) {
      // extendemos el tipo de sesión con role y accessToken
      // @ts-ignore – NextAuth por defecto no conoce "role"
      (session.user as any).role = (token.role as any) ?? "USER";
      // @ts-ignore – añadimos accessToken a la sesión
      (session as any).accessToken =
      (token.accessToken as string | undefined) ?? undefined;
      return session;
    },
  },
};

// --------------------------------------------------------------------------
// LEGACY: authorize contra FastAPI (lo dejo guardado por si lo reactivas luego)
// --------------------------------------------------------------------------
//
// Si en el futuro quieres volver al backend, puedes reemplazar el authorize()
// de arriba por esta versión que tenías antes adaptada a /login/access-token:
//
// const API_BASE_URL = process.env.INTERNAL_API_URL ?? process.env.API_BASE_URL;
//
// async authorize(credentials) {
//   if (!credentials?.email || !credentials?.password || !API_BASE_URL) return null;
//
//   // 1) Login FastAPI estilo OAuth2PasswordRequestForm:
//   //    POST /api/v1/login/access-token (x-www-form-urlencoded, username/password)
//   const res = await fetch(`${API_BASE_URL}/login/access-token`, {
//     method: "POST",
//     headers: { "Content-Type": "application/x-www-form-urlencoded" },
//     body: new URLSearchParams({
//       username: credentials.email as string,
//       password: credentials.password as string,
//     }),
//   });
//
//   if (!res.ok) {
//     // Si tu backend usa otra ruta, avísame y lo ajustamos;
//     // de momento devolvemos null → CredentialsSignin
//     return null;
//   }
//
//   // Esperado: { access_token, token_type?, user? }
//   const raw = await res.json();
//   let user = raw?.user as
//     | { id?: number | string; email?: string; name?: string; role?: "ADMIN" | "USER" }
//     | undefined;
//
//   // 2) Si la respuesta no trae user, intenta /users/me o /login/me con el token
//   if (!user && raw?.access_token) {
//     const tryPaths = [`${API_BASE_URL}/users/me`, `${API_BASE_URL}/login/me`];
//     for (const url of tryPaths) {
//       try {
//         const me = await fetch(url, {
//           headers: { Authorization: `Bearer ${raw.access_token}` },
//         });
//         if (me.ok) {
//           user = await me.json();
//           break;
//         }
//       } catch {
//         // sigue al siguiente
//       }
//     }
//   }
//
//   // 3) Normaliza el objeto user para NextAuth
//   const id = user?.id ?? user?.email ?? credentials.email;
//   const email = user?.email ?? credentials.email;
//   const name = user?.name ?? email;
//   const role = (user?.role ?? "USER") as "ADMIN" | "USER";
//   const accessToken = raw?.access_token as string | undefined;
//
//   return { id, email, name, role, accessToken };
// }
