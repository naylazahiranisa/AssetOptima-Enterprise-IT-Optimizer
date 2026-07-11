"use client";

import { FileText } from "lucide-react";
import { cn } from "@/lib/utils";

interface CitationBadgeProps {
  index: number;
  title: string;
  onClick?: () => void;
  className?: string;
}

/** Clickable citation reference badge shown inline in AI responses */
export function CitationBadge({
  index,
  title,
  onClick,
  className,
}: CitationBadgeProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={title}
      className={cn(
        "text-primary hover:bg-primary/10 border-primary/30 inline-flex h-4 min-w-4 items-center justify-center rounded border px-1 text-[10px] font-medium transition-colors",
        className,
      )}
    >
      {index}
    </button>
  );
}
