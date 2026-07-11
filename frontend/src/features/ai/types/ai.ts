export type MessageRole = "user" | "assistant" | "system";

export type MessageStatus = "sending" | "streaming" | "complete" | "error";

export interface Citation {
  id: string;
  title: string;
  snippet: string;
  source: string;
  score: number;
}

export interface AIMessage {
  id: string;
  role: MessageRole;
  content: string;
  status: MessageStatus;
  citations?: Citation[];
  confidence?: number;
  sources?: string[];
  timestamp: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: AIMessage[];
  created_at: string;
  updated_at: string;
  pinned: boolean;
  model?: string;
}

export interface AISettings {
  temperature: number;
  topK: number;
  chunkSize: number;
  modelVersion: string;
}

export interface SourceDocument {
  id: string;
  title: string;
  type: "pdf" | "csv" | "doc" | "txt";
  size: string;
  chunks: number;
  lastIndexed: string;
  preview?: string;
}

export interface RetrievedChunk {
  id: string;
  content: string;
  source: string;
  score: number;
  metadata: Record<string, string>;
}

export interface SendMessagePayload {
  content: string;
  conversationId?: string;
  signal?: AbortSignal;
}

export interface StreamChunk {
  type: "token" | "citation" | "source" | "done" | "error";
  content: string;
  citations?: Citation[];
  sources?: string[];
}

export interface CreateConversationPayload {
  title?: string;
}

export type AIErrorCode =
  "RAG_UNAVAILABLE" | "CONTEXT_TOO_LARGE" | "RATE_LIMITED" | "INVALID_QUERY";

export interface AIError {
  code: AIErrorCode;
  message: string;
}
