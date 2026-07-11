"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface PromptCardProps {
  label: string;
  onClick: () => void;
  index?: number;
  className?: string;
}

/** Clickable suggested question card shown in the chat area */
export function PromptCard({
  label,
  onClick,
  index = 0,
  className,
}: PromptCardProps) {
  return (
    <motion.button
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.04 }}
      type="button"
      onClick={onClick}
      className={cn(
        "group border-border bg-card hover:border-primary/30 hover:bg-muted/50 flex w-full items-start gap-3 rounded-xl border p-4 text-left transition-all",
        className,
      )}
    >
      <div className="text-primary/60 group-hover:text-primary mt-0.5 shrink-0 transition-colors">
        <Sparkles size={14} />
      </div>
      <p className="text-foreground group-hover:text-foreground text-sm leading-snug">
        {label}
      </p>
    </motion.button>
  );
}
