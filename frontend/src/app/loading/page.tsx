"use client";

import { Loader2, HardDrive } from "lucide-react";

export default function LoadingPage() {
  return (
    <div className="bg-background flex min-h-screen flex-col items-center justify-center">
      <div className="bg-primary flex h-12 w-12 items-center justify-center rounded-xl shadow-sm">
        <HardDrive size={24} className="text-primary-foreground" />
      </div>
      <Loader2 size={20} className="text-primary mt-4 animate-spin" />
      <p className="text-muted-foreground mt-3 text-sm">
        Verifying your session...
      </p>
    </div>
  );
}
