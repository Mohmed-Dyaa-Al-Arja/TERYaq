import { createFileRoute } from "@tanstack/react-router";
import { Trash2 } from "lucide-react";
import { AppShell } from "@/components/app/AppShell";
import { AnswerCard } from "@/components/app/AnswerCard";
import { formatRelative, useStore } from "@/lib/store";

export const Route = createFileRoute("/saved")({
  head: () => ({
    meta: [
      { title: "Saved Evidence | TERYaq" },
      {
        name: "description",
        content: "Your bookmarked clinical answers with their supporting evidence and references.",
      },
      { property: "og:title", content: "Saved Evidence | TERYaq" },
      {
        property: "og:description",
        content: "Bookmarked clinical answers with traceable references.",
      },
    ],
  }),
  component: SavedPage,
});

function SavedPage() {
  const { saved, removeSaved, hydrated } = useStore();

  return (
    <AppShell
      title="Saved Evidence"
      subtitle="Answers you bookmarked together with their clinical references."
      action={
        <span className="rounded-lg bg-muted px-3 py-1.5 text-xs sm:text-sm">
          {saved.length} saved
        </span>
      }
    >
      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-8">
        <div className="mx-auto max-w-4xl space-y-5">
          {hydrated && saved.length === 0 && (
            <p className="rounded-2xl border border-dashed border-border p-10 text-center text-sm text-muted-foreground">
              Nothing saved yet — use “Save Evidence” on any answer.
            </p>
          )}
          {saved.map((s) => (
            <section key={s.id} className="space-y-2">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <h2 className="font-display text-lg font-semibold">{s.question}</h2>
                  <p className="text-xs text-muted-foreground">Saved {formatRelative(s.savedAt)}</p>
                </div>
                <button
                  type="button"
                  aria-label="Remove saved evidence"
                  onClick={() => removeSaved(s.id)}
                  className="shrink-0 rounded-lg border border-border p-2 text-muted-foreground transition-colors hover:border-destructive/40 hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              <AnswerCard answer={s.answer} question={s.question} onSave={() => {}} compact />
            </section>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
