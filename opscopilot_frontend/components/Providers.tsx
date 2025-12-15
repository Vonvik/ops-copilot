"use client";

import { SessionProvider } from "next-auth/react";
import type { ReactNode } from "react";

type Props = { children: ReactNode };

// Export nombrado (por si lo necesitas)
export function Providers({ children }: Props) {
  return <SessionProvider>{children}</SessionProvider>;
}

// Export por defecto (lo que usas en layout)
export default Providers;
