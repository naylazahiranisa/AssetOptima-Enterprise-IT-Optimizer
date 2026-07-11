"use client";

import { useState, type ReactNode } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopNav } from "@/components/layout/TopNav";
import { Footer } from "@/components/layout/Footer";
import { AuthGuard } from "@/features/auth/AuthGuard";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const isAiPage = pathname === "/ai-assistant";
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <AuthGuard>
      <div className="bg-background flex h-screen overflow-hidden">
        <Sidebar
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          isCollapsed={sidebarCollapsed}
          onCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        <div className="flex flex-1 flex-col overflow-hidden">
          <TopNav onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />

          <main
            className={
              isAiPage
                ? "flex-1 overflow-hidden p-0"
                : "flex-1 overflow-y-auto px-6 py-8 lg:px-8"
            }
          >
            {children}
          </main>

          <Footer />
        </div>
      </div>
    </AuthGuard>
  );
}
