"use client";

import { useState, useRef, useCallback, type KeyboardEvent } from "react";
import { motion } from "framer-motion";
import { Send, Square, Upload, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop?: () => void;
  onClear?: () => void;
  onUpload?: (file: File) => void;
  isGenerating?: boolean;
  disabled?: boolean;
  className?: string;
}

/** Chat prompt input with send, stop, upload, and character counter */
export function ChatInput({
  onSend,
  onStop,
  onClear,
  onUpload,
  isGenerating = false,
  disabled = false,
  className,
}: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const MAX_CHARS = 2000;

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || isGenerating || disabled) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, isGenerating, disabled, onSend]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  };

  const handleFilePick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onUpload) {
      onUpload(file);
    }
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const charsLeft = MAX_CHARS - value.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "border-border bg-card rounded-2xl border p-2 shadow-sm",
        className,
      )}
    >
      <div className="flex items-end gap-2">
        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your assets, licenses, or policies..."
            rows={1}
            disabled={disabled || isGenerating}
            maxLength={MAX_CHARS}
            className="text-foreground placeholder:text-muted-foreground/50 max-h-[200px] min-h-[44px] w-full resize-none rounded-xl border-0 bg-transparent px-3 py-3 text-sm outline-none disabled:opacity-50"
          />
        </div>

        <div className="flex items-center gap-1 pb-1">
          {onUpload && (
            <>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.csv,.doc,.docx,.txt"
                className="hidden"
                onChange={handleFileChange}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="text-muted-foreground hover:text-foreground h-8 w-8"
                onClick={handleFilePick}
                title="Upload document"
              >
                <Upload size={14} />
              </Button>
            </>
          )}

          {isGenerating && onStop ? (
            <Button
              type="button"
              variant="outline"
              size="icon"
              className="border-danger/30 text-danger hover:bg-danger/10 h-9 w-9"
              onClick={onStop}
              title="Stop generating"
            >
              <Square size={14} />
            </Button>
          ) : (
            <Button
              type="button"
              size="icon"
              className="h-9 w-9"
              onClick={handleSend}
              disabled={!value.trim() || disabled}
            >
              <Send size={14} />
            </Button>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between px-3 pb-1">
        <div className="flex items-center gap-2">
          {onClear && value && (
            <button
              type="button"
              onClick={onClear}
              className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-[11px] transition-colors"
            >
              <X size={10} />
              Clear
            </button>
          )}
        </div>
        <div
          className={cn(
            "text-[10px] transition-colors",
            charsLeft < 50 ? "text-danger" : "text-muted-foreground",
          )}
        >
          {charsLeft}
        </div>
      </div>
    </motion.div>
  );
}
