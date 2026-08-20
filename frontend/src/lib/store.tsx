import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { ChatAnswer, Conversation, SavedEvidence } from "./types";
import { mockConversations } from "./mock-data";
import { API_BASE_URL } from "@/services/chatApi";

/**
 * Client-side app state (conversations + saved evidence), persisted to
 * localStorage. Swap the read/write helpers for API calls when your backend
 * exposes conversation persistence.
 */

const CONV_KEY = "teryaq.conversations";
const SAVED_KEY = "teryaq.saved";

function read<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

export const uid = () => Math.random().toString(36).slice(2, 10);

interface StoreValue {
  hydrated: boolean;
  activeId: string | null;
  setActiveId: (id: string | null) => void;
  conversations: Conversation[];
  saved: SavedEvidence[];
  setConversations: (updater: (prev: Conversation[]) => Conversation[]) => void;
  createConversation: () => Conversation;
  deleteConversation: (id: string) => void;
  saveEvidence: (question: string, answer: ChatAnswer) => void;
  removeSaved: (id: string) => void;
}

const StoreContext = createContext<StoreValue | null>(null);

export function StoreProvider({ children }: { children: ReactNode }) {
  const [hydrated, setHydrated] = useState(false);
  const [conversations, setConvs] = useState<Conversation[]>([]);
  const [saved, setSaved] = useState<SavedEvidence[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  useEffect(() => {
    const stored = read<Conversation[] | null>(CONV_KEY, null);
    // Seed with mock conversations only while no backend is configured.
    setConvs(stored ?? (API_BASE_URL ? [] : mockConversations));
    setSaved(read<SavedEvidence[]>(SAVED_KEY, []));
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated) window.localStorage.setItem(CONV_KEY, JSON.stringify(conversations));
  }, [conversations, hydrated]);

  useEffect(() => {
    if (hydrated) window.localStorage.setItem(SAVED_KEY, JSON.stringify(saved));
  }, [saved, hydrated]);

  const setConversations = useCallback(
    (updater: (prev: Conversation[]) => Conversation[]) => setConvs(updater),
    [],
  );

  const createConversation = useCallback(() => {
    const conv: Conversation = {
      id: uid(),
      title: "New conversation",
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messages: [],
    };
    setConvs((prev) => [conv, ...prev]);
    setActiveId(conv.id);
    return conv;
  }, []);

  const deleteConversation = useCallback(
    (id: string) => setConvs((prev) => prev.filter((c) => c.id !== id)),
    [],
  );

  const saveEvidence = useCallback((question: string, answer: ChatAnswer) => {
    setSaved((prev) => [{ id: uid(), question, answer, savedAt: Date.now() }, ...prev]);
  }, []);

  const removeSaved = useCallback(
    (id: string) => setSaved((prev) => prev.filter((s) => s.id !== id)),
    [],
  );

  const value = useMemo(
    () => ({
      hydrated,
      activeId,
      setActiveId,
      conversations,
      saved,
      setConversations,
      createConversation,
      deleteConversation,
      saveEvidence,
      removeSaved,
    }),
    [
      hydrated,
      activeId,
      conversations,
      saved,
      setConversations,
      createConversation,
      deleteConversation,
      saveEvidence,
      removeSaved,
    ],
  );

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}

export function useStore() {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error("useStore must be used inside <StoreProvider>");
  return ctx;
}

export function formatRelative(ts: number) {
  const diff = Date.now() - ts;
  const mins = Math.round(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const d = new Date(ts);
  const time = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  if (diff < 1000 * 60 * 60 * 24) return `Today · ${time}`;
  return `${d.toLocaleDateString()} · ${time}`;
}
