import NextAuth, { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: {
      id?: string | number | null;
      role?: "ADMIN" | "USER";
    } & DefaultSession["user"];
    accessToken?: string;
  }

  interface User {
    id?: string | number | null;
    role?: "ADMIN" | "USER";
    accessToken?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    sub?: string;
    role?: "ADMIN" | "USER";
    accessToken?: string;
  }
}
