"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/services/api";
import type {
  AIMessage,
  Conversation,
  AISettings,
  SourceDocument,
  RetrievedChunk,
  SendMessagePayload,
  CreateConversationPayload,
  Citation,
} from "@/features/ai/types/ai";

const STORAGE_KEY = "assetoptima_conversations";

function loadConversations(): Conversation[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveConversations(convs: Conversation[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(convs));
}

export function useConversations() {
  const queryClient = useQueryClient();
  return useQuery<Conversation[]>({
    queryKey: ["ai", "conversations"],
    queryFn: async () => {
      return loadConversations();
    },
    staleTime: 0,
    refetchOnWindowFocus: true,
  });
}

export function useConversation(id: string | null) {
  return useQuery<Conversation | null>({
    queryKey: ["ai", "conversations", id],
    queryFn: async () => {
      if (!id) return null;
      const convs = loadConversations();
      return convs.find((c) => c.id === id) ?? null;
    },
    staleTime: 0,
    enabled: !!id,
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: SendMessagePayload) => {
      const res = await api.post(
        "/api/v1/ai/chat",
        {
          question: payload.content,
          top_k: 5,
          domain: null,
        },
        {
          signal: payload.signal,
        },
      );
      const data = (res.data as any).data ?? res.data;
      const answer = data?.answer ?? data?.content ?? "";
      const sources = data?.source_documents ?? data?.sources ?? [];
      const confidence = data?.confidence ?? 0;

      const citations: Citation[] = sources.map((s: any, i: number) => ({
        id: `cit-${i}`,
        title: s.title ?? s.name ?? `Source ${i + 1}`,
        snippet: typeof s === "string" ? s : s.snippet ?? s.content ?? "",
        source: s.source ?? s.filename ?? "",
        score: s.score ?? s.confidence ?? 0,
      }));

      const msg: AIMessage = {
        id: `msg-${Date.now()}`,
        role: "assistant",
        content: answer,
        status: "complete",
        citations: citations.length > 0 ? citations : undefined,
        confidence,
        sources: sources.map(
          (s: any) => s.title ?? s.name ?? s.filename ?? "",
        ),
        timestamp: new Date().toISOString(),
      };

      return msg;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai", "conversations"] });
    },
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateConversationPayload) => {
      const conv: Conversation = {
        id: `conv-${Date.now()}`,
        title: payload.title ?? "New Conversation",
        messages: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        pinned: false,
      };
      const convs = loadConversations();
      convs.unshift(conv);
      saveConversations(convs);
      return conv;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai", "conversations"] });
    },
  });
}

export function useDeleteConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const convs = loadConversations().filter((c) => c.id !== id);
      saveConversations(convs);
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai", "conversations"] });
    },
  });
}

export function useTogglePinConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, pinned }: { id: string; pinned: boolean }) => {
      const convs = loadConversations().map((c) =>
        c.id === id ? { ...c, pinned: !pinned } : c,
      );
      saveConversations(convs);
      return { id, pinned: !pinned };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai", "conversations"] });
    },
  });
}

export function useRenameConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, title }: { id: string; title: string }) => {
      const convs = loadConversations().map((c) =>
        c.id === id ? { ...c, title } : c,
      );
      saveConversations(convs);
      return { id, title };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai", "conversations"] });
    },
  });
}

export function useAISettings() {
  return useQuery<AISettings>({
    queryKey: ["ai", "settings"],
    queryFn: async () => {
      return {
        temperature: 0.3,
        topK: 5,
        chunkSize: 512,
        modelVersion: "AssetOptima-RAG-v1",
      };
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useUpdateAISettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (settings: Partial<AISettings>) => {
      return settings;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai", "settings"] });
    },
  });
}

export function useSources() {
  return useQuery<SourceDocument[]>({
    queryKey: ["ai", "sources"],
    queryFn: async () => {
      return [];
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useRetrievedChunks() {
  return useQuery<RetrievedChunk[]>({
    queryKey: ["ai", "chunks"],
    queryFn: async () => {
      return [];
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useClearConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const convs = loadConversations().map((c) =>
        c.id === id ? { ...c, messages: [] } : c,
      );
      saveConversations(convs);
      return { success: true };
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["ai", "conversations", id] });
    },
  });
}

/** Save messages to a conversation in localStorage */
export function saveMessagesToConversation(
  convId: string,
  messages: AIMessage[],
) {
  const convs = loadConversations().map((c) => {
    if (c.id === convId) {
      const title =
        c.messages.length === 0 && messages.length > 0
          ? messages[0].content.slice(0, 60) + (messages[0].content.length > 60 ? "..." : "")
          : c.title;
      return {
        ...c,
        title,
        messages,
        updated_at: new Date().toISOString(),
      };
    }
    return c;
  });
  saveConversations(convs);
}
