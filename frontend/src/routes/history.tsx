import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { FileText, Search, Trash2 } from "lucide-react";
import { AppShell } from "@/components/app/AppShell";
import { formatRelative, useStore } from "@/lib/store";
import type { EvidenceStatus } from "@/lib/types";
import { EvidenceBadge } from "@/components/app/EvidenceBadge";

export const Route = createFileRoute("/history")({
  head: () => ({
    meta: [
      { title: "Conversation History | TERYaq" },
      {
        name: "description",
        content: "Review previous evidence-grounded clinical questions and answers.",
      },
      { property: "og:title", content: "Conversation History | TERYaq" },
      {
        property: "og:description",
        content: "Browse and search your past clinical evidence conversations.",
      },
    ],
  }),
  component: HistoryPage,
});

function HistoryPage() {
  const { conversations, setActiveId, deleteConversation, hydrated } = useStore();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("all");

  const rows = useMemo(
    () =>
      conversations
        .map((c) => {
          const answer = c.messages.find((m) => m.answer)?.answer;
          return { conv: c, answer };
        })
        .filter(({ conv, answer }) => {
          const q = query.trim().toLowerCase();
          const matchQ =
            !q ||
            conv.title.toLowerCase().includes(q) ||
            (answer?.answer ?? "").toLowerCase().includes(q);
          const matchL = level === "all" || answer?.evidence_status === level;
          return matchQ && matchL;
        }),
    [conversations, query, level],
  );

  return (
    <AppShell
      title="Conversation History"
      subtitle="Review previous evidence-grounded clinical questions and answers."
      action={
        <span className="rounded-lg bg-muted px-3 py-1.5 text-xs sm:text-sm">
          {conversations.length} conversations
        </span>
      }
    >
      <div className="border-b border-border px-4 py-4 sm:px-8">
        <div className="mx-auto flex max-w-5xl flex-col gap-3 sm:flex-row">
          <div className="flex min-w-0 flex-1 items-center gap-2 rounded-xl border border-border bg-card px-4">
            <Search className="h-4 w-4 shrink-0 text-muted-foreground" aria-hidden />
            <label htmlFor="search" className="sr-only">
              Search questions and answers
            </label>
            <input
              id="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search questions and answers..."
              className="min-w-0 flex-1 bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground"
            />
          </div>
          <label htmlFor="level" className="sr-only">
            Filter by evidence level
          </label>
          <select
            id="level"
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="rounded-xl border border-border bg-card px-4 py-3 text-sm outline-none"
          >
            <option value="all">All evidence levels</option>
            {(["Strong", "Moderate", "Limited", "Insufficient"] as EvidenceStatus[]).map((s) => (
              <option key={s} value={s}>
                {s} evidence
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-8">
        <ul className="mx-auto max-w-5xl space-y-4">
          {hydrated && rows.length === 0 && (
            <li className="rounded-2xl border border-dashed border-border p-10 text-center text-sm text-muted-foreground">
              {conversations.length === 0
                ? "No conversations yet — start one from the Chat tab."
                : "No results match your search."}
            </li>
          )}
          {rows.map(({ conv, answer }) => (
            <li
              key={conv.id}
              className="rounded-2xl border border-border bg-card p-5 shadow-card transition-colors hover:border-teal/40"
            >
              <div className="flex items-start justify-between gap-4">
                <button
                  type="button"
                  onClick={() => {
                    setActiveId(conv.id);
                    navigate({ to: "/" });
                  }}
                  className="min-w-0 flex-1 text-left"
                >
                  <h2 className="font-display text-lg leading-snug font-semibold">{conv.title}</h2>
                  {answer && (
                    <p className="mt-1.5 line-clamp-2 text-sm text-muted-foreground">
                      {answer.answer}
                    </p>
                  )}
                  <div className="mt-3 flex flex-wrap items-center gap-3">
                    {answer && <EvidenceBadge status={answer.evidence_status} />}
                    <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <FileText className="h-3.5 w-3.5" aria-hidden />
                      {answer?.citations.length ?? 0} sources
                    </span>
                  </div>
                </button>
                <div className="flex shrink-0 flex-col items-end gap-3">
                  <span className="text-xs text-muted-foreground">
                    {formatRelative(conv.updatedAt)}
                  </span>
                  <button
                    type="button"
                    aria-label={`Delete conversation: ${conv.title}`}
                    onClick={() => deleteConversation(conv.id)}
                    className="rounded-lg border border-border p-2 text-muted-foreground transition-colors hover:border-destructive/40 hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </AppShell>
  );
}
