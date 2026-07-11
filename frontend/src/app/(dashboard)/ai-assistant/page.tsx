"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { RefreshCw, Menu, Bot, Settings, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { ChatBubble } from "@/features/ai/components/ChatBubble";
import { ChatInput } from "@/features/ai/components/ChatInput";
import { ConversationList } from "@/features/ai/components/ConversationList";
import { PromptCard } from "@/features/ai/components/PromptCard";
import { TypingIndicator } from "@/features/ai/components/TypingIndicator";
import { AIStatusBadge } from "@/features/ai/components/AIStatusBadge";
import {
  useConversations,
  useConversation,
  useSendMessage,
  useCreateConversation,
  useDeleteConversation,
  useTogglePinConversation,
  useRenameConversation,
  useClearConversation,
  saveMessagesToConversation,
} from "@/features/ai/services/ai.service";
import type { AIMessage } from "@/features/ai/types/ai";

const SUGGESTIONS = [
  "How many assets do we have?",
  "Show laptops assigned to the Finance department",
  "Which software licenses are inactive?",
  "List employees by department",
  "How many Microsoft 365 licenses are unused?",
  "What assets require maintenance?",
];

export default function AiAssistantPage() {
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [localMessages, setLocalMessages] = useState<AIMessage[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const { data: conversations = [], refetch: refetchConversations } =
    useConversations();
  const { data: activeConversation, refetch: refetchActiveConversation } =
    useConversation(activeConvId);

  const messages =
    activeConversation?.messages && activeConversation.messages.length > 0
      ? activeConversation.messages
      : localMessages;
  const sendMessage = useSendMessage();
  const createConversation = useCreateConversation();
  const deleteConversation = useDeleteConversation();
  const togglePin = useTogglePinConversation();
  const renameConversation = useRenameConversation();
  const clearConversation = useClearConversation();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Sync local messages to conversation when activeConversation changes
  useEffect(() => {
    if (activeConvId && activeConversation) {
      if (
        activeConversation.messages.length > 0 &&
        localMessages.length === 0
      ) {
        setLocalMessages(activeConversation.messages);
      }
    }
  }, [activeConvId, activeConversation, localMessages.length]);

  const abortRef = useRef<AbortController | null>(null);

  const persistMessages = useCallback(
    (msgs: AIMessage[]) => {
      if (activeConvId) {
        saveMessagesToConversation(activeConvId, msgs);
        refetchConversations();
        refetchActiveConversation();
      }
    },
    [activeConvId, refetchConversations, refetchActiveConversation],
  );

  const handleSend = useCallback(
    async (content: string) => {
      // Auto-create conversation if none active
      let convId = activeConvId;
      if (!convId) {
        const conv = await createConversation.mutateAsync({});
        convId = conv.id;
        setActiveConvId(convId);
      }

      const userMsg: AIMessage = {
        id: `msg-${Date.now()}`,
        role: "user",
        content,
        status: "complete",
        timestamp: new Date().toISOString(),
      };

      const placeholderMsg: AIMessage = {
        id: `msg-response-${Date.now()}`,
        role: "assistant",
        content: "",
        status: "streaming",
        timestamp: new Date().toISOString(),
      };

      const newMessages = [...localMessages, userMsg, placeholderMsg];
      setLocalMessages(newMessages);
      setIsGenerating(true);

      abortRef.current = new AbortController();

      try {
        const response = await sendMessage.mutateAsync({
          content,
          conversationId: convId ?? undefined,
          signal: abortRef.current.signal,
        });

        const finalMessages = [
          ...localMessages,
          userMsg,
          { ...response, status: "complete" as const },
        ];
        setLocalMessages(finalMessages);
        persistMessages(finalMessages);
      } catch {
        const errorMsg: AIMessage = {
          ...placeholderMsg,
          content: "Sorry, I encountered an error processing your request.",
          status: "error" as const,
        };
        const finalMessages = [...localMessages, userMsg, errorMsg];
        setLocalMessages(finalMessages);
        persistMessages(finalMessages);
      } finally {
        setIsGenerating(false);
        abortRef.current = null;
      }
    },
    [
      activeConvId,
      localMessages,
      sendMessage,
      createConversation,
      persistMessages,
    ],
  );

  const handleStop = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
    setLocalMessages((prev) =>
      prev.map((m) =>
        m.status === "streaming"
          ? {
              ...m,
              content: m.content || "Response cancelled.",
              status: "error" as const,
            }
          : m,
      ),
    );
    setIsGenerating(false);
  }, []);

  const handleNewConversation = useCallback(async () => {
    const conv = await createConversation.mutateAsync({});
    setActiveConvId(conv.id);
    setLocalMessages([]);
    setMobileSidebarOpen(false);
  }, [createConversation]);

  const handleSelectConversation = useCallback(
    (id: string) => {
      setActiveConvId(id);
      setLocalMessages([]);
      setMobileSidebarOpen(false);
    },
    [],
  );

  const handleClear = useCallback(() => {
    setLocalMessages([]);
    if (activeConvId) {
      clearConversation.mutate(activeConvId);
    }
  }, [activeConvId, clearConversation]);

  const handleSuggestionClick = useCallback(
    (suggestion: string) => {
      handleSend(suggestion);
    },
    [handleSend],
  );

  return (
    <div className="flex h-full gap-0">
      {/* Mobile sidebar */}
      <Sheet open={mobileSidebarOpen} onOpenChange={setMobileSidebarOpen}>
        <SheetContent side="left" className="w-72 p-0">
          <SheetHeader className="border-border border-b px-4 py-3">
            <SheetTitle className="flex items-center gap-2 text-sm">
              <Bot size={16} className="text-ai" />
              Conversations
            </SheetTitle>
          </SheetHeader>
          <ConversationList
            conversations={conversations}
            activeId={activeConvId}
            onSelect={handleSelectConversation}
            onNew={handleNewConversation}
            onDelete={(id) => {
              deleteConversation.mutate(id);
              if (activeConvId === id) {
                setActiveConvId(null);
                setLocalMessages([]);
              }
            }}
            onRename={(id, title) =>
              renameConversation.mutate({ id, title })
            }
            onTogglePin={(id, pinned) => togglePin.mutate({ id, pinned })}
          />
        </SheetContent>
      </Sheet>

      {/* Desktop conversation sidebar */}
      <aside className="border-border bg-card hidden w-64 shrink-0 flex-col border-r lg:flex">
        <ConversationList
          conversations={conversations}
          activeId={activeConvId}
          onSelect={handleSelectConversation}
          onNew={handleNewConversation}
          onDelete={(id) => {
            deleteConversation.mutate(id);
            if (activeConvId === id) {
              setActiveConvId(null);
              setLocalMessages([]);
            }
          }}
          onRename={(id, title) =>
            renameConversation.mutate({ id, title })
          }
          onTogglePin={(id, pinned) => togglePin.mutate({ id, pinned })}
        />
      </aside>

      {/* Main chat area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Chat header */}
        <div className="border-border flex shrink-0 items-center justify-between border-b px-4 py-3">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="text-muted-foreground hover:text-foreground -ml-1 rounded-lg p-1 lg:hidden"
            >
              <Menu size={18} />
            </button>
            <div className="flex items-center gap-2">
              <div className="bg-ai/10 text-ai flex h-8 w-8 items-center justify-center rounded-lg">
                <Bot size={16} />
              </div>
              <div>
                <h1 className="text-foreground text-sm font-semibold">
                  AssetOptima AI
                </h1>
                <p className="text-muted-foreground text-[10px]">
                  RAG-powered assistant
                </p>
              </div>
            </div>
            <AIStatusBadge status="connected" />
          </div>

          <div className="flex items-center gap-1">
            <Badge
              variant="outline"
              className="text-muted-foreground hidden gap-1 px-2 text-[10px] sm:inline-flex"
            >
              AssetOptima-RAG-v1
            </Badge>

            {messages.length > 0 && (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={handleClear}
                title="Clear conversation"
              >
                <Trash2 size={14} />
              </Button>
            )}

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Settings size={14} />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <div className="px-3 py-2">
                  <p className="text-foreground text-xs font-medium">
                    AI Settings
                  </p>
                </div>
                <Separator />
                <div className="space-y-3 px-3 py-2">
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-muted-foreground">
                        Temperature
                      </span>
                      <span className="text-foreground">0.3</span>
                    </div>
                    <div className="bg-muted h-1 rounded-full">
                      <div className="bg-primary h-1 w-[30%] rounded-full" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-muted-foreground">
                      Top-K Retrieval
                    </span>
                    <span className="text-foreground">5</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-muted-foreground">Chunk Size</span>
                    <span className="text-foreground">512</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-muted-foreground">Model</span>
                    <span className="text-foreground">v1.0</span>
                  </div>
                </div>
                <Separator />
                <DropdownMenuItem className="text-danger gap-2 text-xs">
                  <RefreshCw size={12} />
                  Reset Context
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-3xl px-4 py-6">
            {messages.length === 0 ? (
              <div className="space-y-8">
                <div className="pt-12 text-center">
                  <div className="bg-ai/10 mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl">
                    <Bot size={28} className="text-ai" />
                  </div>
                  <h2 className="text-foreground text-lg font-semibold">
                    How can I help you today?
                  </h2>
                  <p className="text-muted-foreground mt-1 text-sm">
                    Ask anything about your IT assets, licenses, and policies
                  </p>
                </div>

                <div className="grid gap-2 sm:grid-cols-2">
                  {SUGGESTIONS.map((s, i) => (
                    <PromptCard
                      key={s}
                      label={s}
                      index={i}
                      onClick={() => handleSuggestionClick(s)}
                    />
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg) => (
                  <ChatBubble key={msg.id} message={msg} />
                ))}

                {isGenerating &&
                  messages[messages.length - 1]?.status === "streaming" && (
                    <TypingIndicator />
                  )}

                <div ref={chatEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input area */}
        <div className="border-border shrink-0 border-t px-4 py-3">
          <div className="mx-auto max-w-3xl">
            <ChatInput
              onSend={handleSend}
              onClear={handleClear}
              onStop={handleStop}
              isGenerating={isGenerating}
            />
            <p className="text-muted-foreground mt-2 text-center text-[10px]">
              AssetOptima AI may display inaccurate info. Verify critical
              decisions with your team.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
