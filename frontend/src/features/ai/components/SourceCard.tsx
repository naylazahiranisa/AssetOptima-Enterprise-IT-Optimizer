"use client";

import { FileText, FileSpreadsheet, File, ExternalLink } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { SourceDocument } from "@/features/ai/types/ai";

interface SourceCardProps {
  source: SourceDocument;
  index?: number;
  className?: string;
}

const typeIcons = {
  pdf: FileText,
  csv: FileSpreadsheet,
  doc: FileText,
  txt: File,
};

/** Document source card displayed in the right source panel */
export function SourceCard({ source, index = 0, className }: SourceCardProps) {
  const Icon = typeIcons[source.type] ?? File;
  return (
    <motion.div
      initial={{ opacity: 0, x: -4 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, delay: index * 0.03 }}
      className={cn(
        "border-border hover:bg-muted/50 group flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors",
        className,
      )}
    >
      <div className="bg-primary/10 text-primary flex h-8 w-8 shrink-0 items-center justify-center rounded-lg">
        <Icon size={14} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-foreground truncate text-sm font-medium">
          {source.title}
        </p>
        <div className="text-muted-foreground mt-0.5 flex items-center gap-2 text-[11px]">
          <span>{source.size}</span>
          <span>·</span>
          <span>{source.chunks} chunks</span>
          <span>·</span>
          <span>{source.lastIndexed}</span>
        </div>
      </div>
      <ExternalLink
        size={12}
        className="text-muted-foreground/40 group-hover:text-muted-foreground mt-1 shrink-0 transition-colors"
      />
    </motion.div>
  );
}
