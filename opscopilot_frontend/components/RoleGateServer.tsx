import { authOptions } from "@/lib/auth";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

export default async function RoleGateServer(
  { children, allow }: { children: React.ReactNode; allow: ("ADMIN" | "USER")[] }
) {
  const session = await getServerSession(authOptions);
  const role = session?.user.role ?? "USER";
  if (!allow.includes(role)) {
    redirect("/dashboard"); // o una página 403
  }
  return <>{children}</>;
}
