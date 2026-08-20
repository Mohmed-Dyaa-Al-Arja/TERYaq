import { useState } from "react";
import { Bookmark, Copy, MessageSquarePlus, Info, FileCheck2, Clock3 } from "lucide-react";
import { toast } from "sonner";
import type { ChatAnswer, Citation } from "@/lib/types";
import { EvidenceBadge, EvidenceMatchRing } from "./EvidenceBadge";
import { EvidenceDetails } from "./EvidenceDetails";
import { cn } from "@/lib/utils";

interface Props {
  answer: ChatAnswer;
  question: string;
  onSave: () => void;
  onFollowUp?: (q: string) => void;
  compact?: boolean;
}

export function AnswerCard({ answer, question, onSave, onFollowUp, compact }: Props) {
  const [active, setActive] = useState<Citation | null>(null);

  const copy = async () => {
    const refs = answer.citations
      .map((c) => `${c.id} · p.${c.page ?? "-"}${c.chunk_id ? ` · ${c.chunk_id}` : ""}`)
      .join("\n");
    await navigator.clipboard.writeText(`${answer.answer}\n\nReferences:\n${refs}`);
    toast.success("Answer copied to clipboard");
  };

  return (
    <article className="rounded-2xl border border-border bg-card p-5 shadow-card sm:p-6">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <EvidenceBadge status={answer.evidence_status} />
            <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <Clock3 className="h-3.5 w-3.5" aria-hidden />
              {[
                answer.evidence_grounded && "Evidence-grounded",
                answer.source_traceable && "Source-traceable",
                answer.reference_backed && "Reference-backed",
              ]
                .filter(Boolean)
                .join(" · ")}
            </span>
          </div>

          <p className="mt-4 leading-relaxed break-words whitespace-pre-wrap text-card-foreground">
            {answer.answer}
          </p>

          <h3 className="sr-only">Source citations</h3>
          <ul className="mt-4 flex flex-wrap gap-2">
            {answer.citations.map((c) => (
              <li key={c.id}>
                <button
                  type="button"
                  onClick={() => setActive(c)}
                  className="rounded-md border border-teal/25 bg-teal-soft/60 px-2.5 py-1 font-mono text-xs text-teal transition-colors hover:border-teal focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
                >
                  {c.id} · p.{c.page ?? "—"}
                  {c.chunk_id ? ` · ${c.chunk_id.slice(-4)}` : ""}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="flex shrink-0 flex-row items-center gap-3 sm:w-32 sm:flex-col sm:text-center">
          <EvidenceMatchRing value={answer.evidence_match} />
          <div>
            <p className="text-[11px] tracking-[0.12em] text-muted-foreground uppercase">
              Evidence match
            </p>
            <p className="text-xs text-muted-foreground">Based on retrieved evidence</p>
          </div>
        </div>
      </div>

      {!compact && (
        <>
          <div className="mt-6 flex flex-wrap items-center gap-2 border-t border-border pt-5">
            <span className="mr-2 text-[11px] tracking-[0.12em] text-muted-foreground uppercase">
              Quick actions
            </span>
            <QuickAction icon={MessageSquarePlus} onClick={() => onFollowUp?.(question)}>
              Explore Chat
            </QuickAction>
            <QuickAction icon={Copy} onClick={copy}>
              Copy Answer
            </QuickAction>
            <QuickAction icon={Bookmark} onClick={onSave}>
              Save Evidence
            </QuickAction>
          </div>

          <div className="mt-4 space-y-2 text-sm">
            <p className="flex flex-wrap items-center gap-2 rounded-lg bg-muted/60 px-3 py-2">
              <FileCheck2 className="h-4 w-4 text-teal" aria-hidden />
              <span className="font-medium">Evidence used to generate this answer</span>
              <span className="rounded-md bg-teal-soft px-2 py-0.5 text-xs text-teal">
                {answer.passed_threshold_count ?? answer.citations.length} passed threshold
              </span>
              <span className="text-xs text-muted-foreground">
                {answer.retrieved_count ?? answer.citations.length} retrieved
              </span>
            </p>
            {answer.next_step && (
              <p className="flex items-start gap-2 rounded-lg bg-muted/60 px-3 py-2 text-muted-foreground">
                <Info className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
                <span>
                  <span className="font-medium text-foreground">Suggested next step</span> —{" "}
                  {answer.next_step}
                </span>
              </p>
            )}
          </div>

          {!!answer.follow_up_questions?.length && onFollowUp && (
            <div className="mt-5">
              <h3 className="text-[11px] tracking-[0.12em] text-muted-foreground uppercase">
                Suggested follow-up questions
              </h3>
              <ul className="mt-2 space-y-2">
                {answer.follow_up_questions.map((q) => (
                  <li key={q}>
                    <button
                      type="button"
                      onClick={() => onFollowUp(q)}
                      className="flex w-full items-center gap-3 rounded-xl border border-border bg-background px-4 py-3 text-left text-sm transition-colors hover:border-teal/50 hover:bg-muted"
                    >
                      <span className="text-teal" aria-hidden>
                        →
                      </span>
                      <span className="min-w-0 flex-1">{q}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      <EvidenceDetails citation={active} onClose={() => setActive(null)} />
    </article>
  );
}

function QuickAction({
  icon: Icon,
  children,
  onClick,
}: {
  icon: React.ElementType;
  children: React.ReactNode;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm transition-colors",
        "hover:border-teal/50 hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none",
      )}
    >
      <Icon className="h-4 w-4 shrink-0" aria-hidden />
      {children}
    </button>
  );
}
