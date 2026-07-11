"use client";

import { useState } from "react";
import {
  PanelRightClose,
  PanelRightOpen,
  Search,
  SlidersHorizontal,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { SourceCard } from "@/features/ai/components/SourceCard";
import { cn } from "@/lib/utils";
import type { SourceDocument, RetrievedChunk } from "@/features/ai/types/ai";

interface SourcePanelProps {
  sources: SourceDocument[];
  chunks: RetrievedChunk[];
  isOpen: boolean;
  onToggle: () => void;
  className?: string;
}

/** Right-side information panel showing retrieved documents, chunks, and settings */
export function SourcePanel({
  sources,
  chunks,
  isOpen,
  onToggle,
  className,
}: SourcePanelProps) {
  const [tab, setTab] = useState<"documents" | "chunks">("documents");

  return (
    <>
      <button
        onClick={onToggle}
        className={cn(
          "text-muted-foreground hover:text-foreground fixed top-4 right-4 z-30 hidden rounded-lg p-2 transition-colors lg:block",
          isOpen && "hidden",
        )}
        title="Open source panel"
      >
        <PanelRightOpen size={18} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 320, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-border bg-card hidden shrink-0 overflow-hidden border-l lg:block"
          >
            <div className="flex h-full w-[320px] flex-col">
              <div className="border-border flex items-center justify-between border-b px-4 py-3">
                <h2 className="text-foreground text-sm font-semibold">
                  Sources
                </h2>
                <button
                  onClick={onToggle}
                  className="text-muted-foreground hover:text-foreground rounded p-1 transition-colors"
                  title="Close panel"
                >
                  <PanelRightClose size={16} />
                </button>
              </div>

              <div className="border-border flex items-center gap-1 border-b px-3 py-2">
                <button
                  onClick={() => setTab("documents")}
                  className={cn(
                    "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                    tab === "documents"
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  Documents
                </button>
                <button
                  onClick={() => setTab("chunks")}
                  className={cn(
                    "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                    tab === "chunks"
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  Chunks
                </button>
                <div className="ml-auto flex items-center gap-1">
                  <Badge variant="primary" className="h-5 px-1.5 text-[10px]">
                    {tab === "documents" ? sources.length : chunks.length}
                  </Badge>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-3">
                {tab === "documents" ? (
                  sources.length > 0 ? (
                    <div className="space-y-2">
                      {sources.map((src, i) => (
                        <SourceCard key={src.id} source={src} index={i} />
                      ))}
                    </div>
                  ) : (
                    <EmptyPanel message="No indexed documents" />
                  )
                ) : (
                  <div className="space-y-2">
                    {chunks.length > 0 ? (
                      chunks.map((chunk, i) => (
                        <ChunkCard key={chunk.id} chunk={chunk} index={i} />
                      ))
                    ) : (
                      <EmptyPanel message="No retrieved chunks" />
                    )}
                  </div>
                )}
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}

function EmptyPanel({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Search
        size={24}
        className="text-muted-foreground/30 mb-3"
        strokeWidth={1.5}
      />
      <p className="text-muted-foreground text-xs">{message}</p>
    </div>
  );
}

function ChunkCard({ chunk, index }: { chunk: RetrievedChunk; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.15, delay: index * 0.02 }}
      className="border-border rounded-lg border p-3"
    >
      <div className="flex items-start justify-between gap-2">
        <p className="text-foreground line-clamp-2 text-xs leading-relaxed">
          {chunk.content}
        </p>
      </div>
      <div className="text-muted-foreground mt-2 flex items-center gap-2 text-[10px]">
        <span className="truncate">{chunk.source}</span>
        <span>·</span>
        <span
          className={cn(
            "font-mono",
            chunk.score > 0.9
              ? "text-success"
              : chunk.score > 0.7
                ? "text-warning"
                : "text-muted-foreground",
          )}
        >
          {Math.round(chunk.score * 100)}%
        </span>
      </div>
    </motion.div>
  );
}
