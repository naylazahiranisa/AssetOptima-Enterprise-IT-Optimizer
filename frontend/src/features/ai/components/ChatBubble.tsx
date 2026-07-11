"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  User,
  Bot,
  Copy,
  Check,
  FileText,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ConfidenceBadge } from "@/features/ai/components/ConfidenceBadge";
import { CitationBadge } from "@/features/ai/components/CitationBadge";
import type { AIMessage, Citation } from "@/features/ai/types/ai";

interface ChatBubbleProps {
  message: AIMessage;
  className?: string;
}

/** Renders a single chat message (user or assistant) with markdown, citations, and sources */
export function ChatBubble({ message, className }: ChatBubbleProps) {
  const [copied, setCopied] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "flex gap-3",
        isUser ? "flex-row-reverse" : "flex-row",
        className,
      )}
    >
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-medium",
          isUser ? "bg-primary text-primary-foreground" : "bg-ai/10 text-ai",
        )}
      >
        {isUser ? <User size={14} /> : <Bot size={14} />}
      </div>

      <div
        className={cn(
          "max-w-[85%] space-y-2",
          isUser && "flex flex-col items-end",
        )}
      >
        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-md"
              : "bg-muted/50 text-foreground rounded-tl-md",
          )}
        >
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <FormattedContent
              content={message.content}
              citations={message.citations}
            />
          </div>
        </div>

        <div className="flex items-center gap-2 px-1">
          {!isUser && message.confidence !== undefined && (
            <ConfidenceBadge score={message.confidence} />
          )}

          {!isUser && message.citations && message.citations.length > 0 && (
            <button
              type="button"
              onClick={() => setShowSources(!showSources)}
              className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-[11px] transition-colors"
            >
              <FileText size={11} />
              {message.citations.length} sources
              {showSources ? (
                <ChevronUp size={11} />
              ) : (
                <ChevronDown size={11} />
              )}
            </button>
          )}

          <button
            type="button"
            onClick={handleCopy}
            className="text-muted-foreground hover:text-foreground ml-auto rounded p-1 transition-colors"
            title="Copy message"
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
          </button>
        </div>

        {!isUser && showSources && message.citations && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="space-y-1.5 overflow-hidden"
          >
            {message.citations.map((cit, i) => (
              <CitationDetail key={cit.id} citation={cit} index={i + 1} />
            ))}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

function CitationDetail({
  citation,
  index,
}: {
  citation: Citation;
  index: number;
}) {
  return (
    <div className="border-border bg-card/50 flex items-start gap-2 rounded-lg border p-2.5 text-xs">
      <CitationBadge index={index} title={citation.title} />
      <div className="min-w-0 flex-1">
        <p className="text-foreground font-medium">{citation.title}</p>
        <p className="text-muted-foreground mt-0.5 line-clamp-1">
          {citation.snippet}
        </p>
      </div>
      <span className="text-muted-foreground shrink-0 font-mono text-[10px]">
        {Math.round(citation.score * 100)}%
      </span>
    </div>
  );
}

/** Renders message content with basic markdown-like formatting */
function FormattedContent({
  content,
  citations,
}: {
  content: string;
  citations?: Citation[];
}) {
  const html = useMemo(() => renderMarkdown(content), [content]);

  return (
    <div
      className="[&_table]:border-border [&_td]:border-border [&_th]:border-border [&_th]:bg-muted/50 [&_tr:not(:last-child)]:border-border [&_blockquote]:border-primary/30 [&_blockquote]:text-muted-foreground [&_code]:bg-muted [&_pre]:bg-muted [&_blockquote]:border-l-2 [&_blockquote]:pl-4 [&_blockquote]:italic [&_code]:rounded [&_code]:px-1 [&_code]:py-0.5 [&_code]:font-mono [&_code]:text-xs [&_li>p]:m-0 [&_ol]:list-decimal [&_ol]:space-y-1 [&_ol]:pl-5 [&_pre]:overflow-x-auto [&_pre]:rounded-lg [&_pre]:p-4 [&_pre_code]:bg-transparent [&_pre_code]:p-0 [&_strong]:font-semibold [&_table]:w-full [&_table]:overflow-hidden [&_table]:rounded-lg [&_table]:border [&_td]:px-3 [&_td]:py-2 [&_td]:text-sm [&_th]:px-3 [&_th]:py-2 [&_th]:text-left [&_th]:text-xs [&_th]:font-medium [&_th]:tracking-wider [&_th]:uppercase [&_tr:not(:last-child)]:border-b [&_ul]:list-disc [&_ul]:space-y-1 [&_ul]:pl-5"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

/** Converts basic markdown to HTML for rendering */
function renderMarkdown(text: string): string {
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  html = html.replace(
    /^### (.+)$/gm,
    "<h3 class='text-base font-semibold mt-4 mb-2'>$1</h3>",
  );
  html = html.replace(
    /^## (.+)$/gm,
    "<h2 class='text-lg font-semibold mt-5 mb-2'>$1</h2>",
  );
  html = html.replace(
    /^# (.+)$/gm,
    "<h1 class='text-xl font-bold mt-5 mb-3'>$1</h1>",
  );

  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  html = html.replace(/^> (.+)$/gm, "<blockquote>$1</blockquote>");

  html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>\n?)+/g, "<ul>$&</ul>");

  html = html.replace(/^\d+\. (.+)$/gm, "<li>$1</li>");

  html = html.replace(
    /\|(.+)\|\n\|[-| ]+\|\n((?:\|.+\|\n?)*)/g,
    (_match: string, header: string, rows: string) => {
      const headers = header
        .split("|")
        .map((h: string) => h.trim())
        .filter(Boolean);
      const rowList = rows
        .trim()
        .split("\n")
        .map((row: string) => {
          const cols = row
            .split("|")
            .map((c: string) => c.trim())
            .filter(Boolean);
          return `<tr>${cols.map((c: string) => `<td>${c}</td>`).join("")}</tr>`;
        })
        .join("");
      return `<table><thead><tr>${headers
        .map((h: string) => `<th>${h}</th>`)
        .join("")}</tr></thead><tbody>${rowList}</tbody></table>`;
    },
  );

  html = html.replace(/\n\n/g, "</p><p>");
  html = html.replace(/\n/g, "<br/>");
  html = `<p>${html}</p>`;
  html = html.replace(/<\/p><p><\/p>/g, "</p><p>");

  return html;
}
