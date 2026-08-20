import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useRef, useState } from "react";
import { AlertCircle, Loader2, ShieldCheck, Stethoscope } from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/app/AppShell";
import { AnswerCard } from "@/components/app/AnswerCard";
import { ChatComposer } from "@/components/app/ChatComposer";
import { useStore, uid } from "@/lib/store";
import { askQuestion } from "@/services/chatApi";
import type { ChatMessage, Conversation } from "@/lib/types";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Clinical Evidence Assistant | TERYaq" },
      {
        name: "description",
        content:
          "Ask breast cancer questions and get evidence-grounded, source-traceable answers backed by trusted clinical references.",
      },
      { property: "og:title", content: "Clinical Evidence Assistant | TERYaq" },
      {
        property: "og:description",
        content: "Evidence-grounded breast cancer answers with traceable clinical citations.",
      },
    ],
  }),
  component: ChatPage,
});

const STARTERS = [
  "What are the potential harms associated with breast cancer screening?",
  "What are the common symptoms of breast cancer?",
  "How often should women aged 40-49 have a mammogram?",
];

function ChatPage() {
  const {
    hydrated,
    conversations,
    setConversations,
    activeId,
    setActiveId,
    createConversation,
    saveEvidence,
  } = useStore();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // ------------------------------------------------------------------
  // Session ID map: conversationId -> backend session_id
  // ------------------------------------------------------------------
  // The backend creates a session on the first request and returns its
  // own session_id.  We keep a local map so every subsequent message
  // in the same conversation sends the correct backend session_id.
  // This enables the LLM to use conversation history for context.
  // ------------------------------------------------------------------
  const sessionIdMap = useRef<Map<string, string>>(new Map());

  const conversation = useMemo<Conversation | undefined>(
    () => conversations.find((c) => c.id === activeId) ?? conversations[0],
    [conversations, activeId],
  );

  useEffect(() => {
    if (hydrated && !activeId && conversation) setActiveId(conversation.id);
  }, [hydrated, activeId, conversation, setActiveId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [conversation?.messages.length, loading]);

  const send = async (question: string) => {
    let convId = conversation?.id;
    if (!convId) convId = createConversation().id;

    const userMsg: ChatMessage = {
      id: uid(),
      role: "user",
      content: question,
      createdAt: Date.now(),
    };

    setConversations((prev) =>
      prev.map((c) =>
        c.id === convId
          ? {
              ...c,
              title: c.messages.length === 0 ? question : c.title,
              updatedAt: Date.now(),
              messages: [...c.messages, userMsg],
            }
          : c,
      ),
    );
    setActiveId(convId);
    setLoading(true);

    try {
      // Use stored backend session_id for this conversation if available.
      const backendSessionId = sessionIdMap.current.get(convId) ?? convId;

      const answer = await askQuestion({
        question,
        conversationId: backendSessionId,
      });

      // If the backend assigned a new session_id, store it.
      const resolvedId = (answer as any)["_resolved_session_id"] as string | undefined;
      if (resolvedId) {
        sessionIdMap.current.set(convId, resolvedId);
      }

      const assistantMsg: ChatMessage = {
        id: uid(),
        role: "assistant",
        content: "",
        createdAt: Date.now(),
        answer,
      };
      setConversations((prev) =>
        prev.map((c) =>
          c.id === convId
            ? { ...c, updatedAt: Date.now(), messages: [...c.messages, assistantMsg] }
            : c,
        ),
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong.";
      setConversations((prev) =>
        prev.map((c) =>
          c.id === convId
            ? {
                ...c,
                messages: [
                  ...c.messages,
                  {
                    id: uid(),
                    role: "assistant",
                    content: "",
                    createdAt: Date.now(),
                    error: message,
                  },
                ],
              }
            : c,
        ),
      );
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const messages = conversation?.messages ?? [];

  return (
    <AppShell
      title="Clinical Evidence Assistant"
      subtitle="Evidence-grounded answers from trusted clinical references"
      action={
        <span className="inline-flex items-center gap-2 rounded-lg border border-teal/30 bg-teal-soft/60 px-3 py-1.5 text-xs text-teal sm:text-sm">
          <span className="h-1.5 w-1.5 rounded-full bg-teal" aria-hidden />
          <span className="hidden sm:inline">Evidence system active</span>
          <span className="sm:hidden">Active</span>
        </span>
      }
    >
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6 sm:px-8">
        <div className="mx-auto flex max-w-4xl flex-col gap-6">
          {hydrated && messages.length === 0 && !loading && (
            <div className="mt-6 rounded-2xl border border-dashed border-border p-8 text-center">
              <Stethoscope className="mx-auto h-8 w-8 text-teal" aria-hidden />
              <h2 className="mt-4 font-display text-2xl">Ask an evidence-grounded question</h2>
              <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
                Every answer is generated from controlled clinical references with traceable
                citations and an evidence-match score.
              </p>
              <ul className="mx-auto mt-6 grid max-w-xl gap-2">
                {STARTERS.map((q) => (
                  <li key={q}>
                    <button
                      type="button"
                      onClick={() => send(q)}
                      className="w-full rounded-xl border border-border bg-card px-4 py-3 text-left text-sm transition-colors hover:border-teal/50"
                    >
                      {q}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {messages.map((m) =>
            m.role === "user" ? (
              <div key={m.id} className="flex justify-end">
                <p className="max-w-[85%] rounded-2xl bg-navy px-5 py-3.5 text-navy-foreground">
                  {m.content}
                </p>
              </div>
            ) : m.error ? (
              <div
                key={m.id}
                role="alert"
                className="flex items-start gap-3 rounded-2xl border border-destructive/30 bg-destructive/5 p-5 text-sm"
              >
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" aria-hidden />
                <div>
                  <p className="font-medium text-destructive">Could not retrieve evidence</p>
                  <p className="mt-1 text-muted-foreground">{m.error}</p>
                </div>
              </div>
            ) : m.answer ? (
              <AnswerCard
                key={m.id}
                answer={m.answer}
                question={conversation?.title ?? ""}
                onFollowUp={(q) => send(q)}
                onSave={() => {
                  saveEvidence(conversation?.title ?? "Saved answer", m.answer!);
                  toast.success("Evidence saved");
                }}
              />
            ) : null,
          )}

          {loading && (
            <div className="flex items-center gap-3 rounded-2xl border border-border bg-card p-5 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin text-teal" aria-hidden />
              Retrieving clinical evidence...
            </div>
          )}

          <p className="flex items-center justify-center gap-2 pt-2 text-xs text-muted-foreground">
            <ShieldCheck className="h-3.5 w-3.5" aria-hidden />
            Educational information only — not a diagnosis or medical advice.
          </p>
        </div>
      </div>

      <ChatComposer value={input} onValueChange={setInput} onSend={send} disabled={loading} />
    </AppShell>
  );
}
