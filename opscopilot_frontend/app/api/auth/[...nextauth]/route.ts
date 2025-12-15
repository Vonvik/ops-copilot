import NextAuth from "next-auth";
import { authOptions } from "@/lib/auth";

// Fuerza runtime Node.js en Next 15 (evita edge/wasm issues)
export const runtime = "nodejs";

// Evita cache en el handler
export const dynamic = "force-dynamic";

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
