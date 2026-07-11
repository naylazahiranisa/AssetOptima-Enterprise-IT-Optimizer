"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquare,
  Pin,
  Trash2,
  Pencil,
  MoreHorizontal,
  Check,
  X,
  Plus,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Conversation } from "@/features/ai/types/ai";

interface ConversationListProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  onRename: (id: string, title: string) => void;
  onTogglePin: (id: string, pinned: boolean) => void;
  className?: string;
}

/** Sidebar list of conversations with pin, rename, delete actions */
export function ConversationList({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
  onRename,
  onTogglePin,
  className,
}: ConversationListProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);

  const pinned = conversations.filter((c) => c.pinned);
  const recent = conversations.filter((c) => !c.pinned);

  const startRename = (conv: Conversation) => {
    setEditingId(conv.id);
    setEditValue(conv.title);
    setOpenMenuId(null);
  };

  const confirmRename = () => {
    if (editingId && editValue.trim()) {
      onRename(editingId, editValue.trim());
    }
    setEditingId(null);
  };

  return (
    <div className={cn("flex h-full flex-col", className)}>
      <div className="p-3">
        <Button size="sm" className="w-full gap-2" onClick={onNew}>
          <Plus size={14} />
          New Conversation
        </Button>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-2 pb-3">
        {pinned.length > 0 && (
          <div className="mb-1 px-2">
            <p className="text-muted-foreground px-1 text-[10px] font-medium tracking-wider uppercase">
              Pinned
            </p>
          </div>
        )}
        {pinned.map((conv) => (
          <ConversationItem
            key={conv.id}
            conversation={conv}
            isActive={conv.id === activeId}
            isEditing={editingId === conv.id}
            editValue={editValue}
            menuOpen={openMenuId === conv.id}
            onSelect={() => onSelect(conv.id)}
            onEditValueChange={setEditValue}
            onStartRename={() => startRename(conv)}
            onConfirmRename={confirmRename}
            onCancelRename={() => setEditingId(null)}
            onDelete={() => onDelete(conv.id)}
            onTogglePin={() => onTogglePin(conv.id, conv.pinned)}
            onOpenMenu={() =>
              setOpenMenuId(openMenuId === conv.id ? null : conv.id)
            }
            onCloseMenu={() => setOpenMenuId(null)}
          />
        ))}

        {recent.length > 0 && (
          <div className={cn("mb-1 px-2", pinned.length > 0 && "mt-4")}>
            <p className="text-muted-foreground px-1 text-[10px] font-medium tracking-wider uppercase">
              Recent
            </p>
          </div>
        )}
        {recent.map((conv) => (
          <ConversationItem
            key={conv.id}
            conversation={conv}
            isActive={conv.id === activeId}
            isEditing={editingId === conv.id}
            editValue={editValue}
            menuOpen={openMenuId === conv.id}
            onSelect={() => onSelect(conv.id)}
            onEditValueChange={setEditValue}
            onStartRename={() => startRename(conv)}
            onConfirmRename={confirmRename}
            onCancelRename={() => setEditingId(null)}
            onDelete={() => onDelete(conv.id)}
            onTogglePin={() => onTogglePin(conv.id, conv.pinned)}
            onOpenMenu={() =>
              setOpenMenuId(openMenuId === conv.id ? null : conv.id)
            }
            onCloseMenu={() => setOpenMenuId(null)}
          />
        ))}

        {conversations.length === 0 && (
          <div className="flex flex-col items-center justify-center py-8">
            <MessageSquare
              size={20}
              className="text-muted-foreground/40 mb-2"
              strokeWidth={1.5}
            />
            <p className="text-muted-foreground text-xs">
              No conversations yet
            </p>
          </div>
        )}
      </nav>
    </div>
  );
}

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  isEditing: boolean;
  editValue: string;
  menuOpen: boolean;
  onSelect: () => void;
  onEditValueChange: (value: string) => void;
  onStartRename: () => void;
  onConfirmRename: () => void;
  onCancelRename: () => void;
  onDelete: () => void;
  onTogglePin: () => void;
  onOpenMenu: () => void;
  onCloseMenu: () => void;
}

function ConversationItem({
  conversation,
  isActive,
  isEditing,
  editValue,
  menuOpen,
  onSelect,
  onEditValueChange,
  onStartRename,
  onConfirmRename,
  onCancelRename,
  onDelete,
  onTogglePin,
  onOpenMenu,
  onCloseMenu,
}: ConversationItemProps) {
  return (
    <div className="relative">
      {isEditing ? (
        <div className="flex items-center gap-1 rounded-lg px-2 py-1.5">
          <input
            value={editValue}
            onChange={(e) => onEditValueChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") onConfirmRename();
              if (e.key === "Escape") onCancelRename();
            }}
            className="text-foreground bg-muted h-7 flex-1 rounded-md border-0 px-2 text-xs outline-none"
            autoFocus
          />
          <button onClick={onConfirmRename} className="text-success p-0.5">
            <Check size={12} />
          </button>
          <button
            onClick={onCancelRename}
            className="text-muted-foreground p-0.5"
          >
            <X size={12} />
          </button>
        </div>
      ) : (
        <button
          onClick={onSelect}
          className={cn(
            "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-xs transition-colors",
            isActive
              ? "bg-primary/10 text-primary font-medium"
              : "text-muted-foreground hover:bg-muted hover:text-foreground",
          )}
        >
          <MessageSquare size={12} className="shrink-0" />
          <span className="truncate">{conversation.title}</span>
          {conversation.pinned && (
            <Pin size={10} className="shrink-0 opacity-50" />
          )}
        </button>
      )}

      {!isEditing && (
        <div className="absolute top-1 right-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              menuOpen ? onCloseMenu() : onOpenMenu();
            }}
            className="text-muted-foreground hover:text-foreground hover:bg-muted rounded p-0.5 opacity-0 transition-opacity group-hover:opacity-100"
            style={menuOpen ? { opacity: 1 } : undefined}
          >
            <MoreHorizontal size={12} />
          </button>

          <AnimatePresence>
            {menuOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={onCloseMenu} />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="bg-card border-border shadow-elevated absolute right-0 z-50 w-36 rounded-lg border py-1"
                >
                  <button
                    onClick={onStartRename}
                    className="hover:bg-muted text-foreground flex w-full items-center gap-2 px-3 py-1.5 text-left text-xs"
                  >
                    <Pencil size={11} />
                    Rename
                  </button>
                  <button
                    onClick={onTogglePin}
                    className="hover:bg-muted text-foreground flex w-full items-center gap-2 px-3 py-1.5 text-left text-xs"
                  >
                    <Pin size={11} />
                    {conversation.pinned ? "Unpin" : "Pin"}
                  </button>
                  <button
                    onClick={onDelete}
                    className="hover:bg-muted text-danger flex w-full items-center gap-2 px-3 py-1.5 text-left text-xs"
                  >
                    <Trash2 size={11} />
                    Delete
                  </button>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
