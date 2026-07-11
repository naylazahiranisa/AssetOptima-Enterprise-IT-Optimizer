import type { ReactNode } from "react";
import { AuthGuard } from "@/features/auth/AuthGuard";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <div className="bg-background relative flex min-h-screen items-center justify-center px-4">
        <div className="absolute inset-0 overflow-hidden">
          <div className="bg-primary/5 absolute -top-40 -right-40 h-80 w-80 rounded-full blur-3xl" />
          <div className="bg-ai/5 absolute -bottom-40 -left-40 h-80 w-80 rounded-full blur-3xl" />
        </div>
        <div className="relative w-full max-w-sm">{children}</div>
      </div>
    </AuthGuard>
  );
}
