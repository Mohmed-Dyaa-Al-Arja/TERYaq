import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import type { Citation } from "@/lib/types";
import { EvidenceMatchRing } from "./EvidenceBadge";

export function EvidenceDetails({
  citation,
  onClose,
}: {
  citation: Citation | null;
  onClose: () => void;
}) {
  return (
    <Sheet open={!!citation} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
        {citation && (
          <>
            <SheetHeader>
              <p className="text-[11px] tracking-[0.14em] text-muted-foreground uppercase">
                Evidence details
              </p>
              <SheetTitle className="font-display text-2xl">{citation.id}</SheetTitle>
            </SheetHeader>

            <div className="space-y-4 px-4 pb-8">
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <Field label="Reference" value={citation.title} />
                <Field label="Source" value={citation.source} />
                <Field label="Publication year" value={citation.year?.toString()} />
                <Field label="Section" value={citation.section} />
                <Field label="Page" value={citation.page?.toString()} />
                <Field label="Chunk ID" value={citation.chunk_id} mono />
              </div>

              {typeof citation.score === "number" && (
                <div className="flex items-center justify-between rounded-xl bg-muted/60 p-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Evidence match</p>
                    <p className="font-display text-3xl text-teal">{citation.score.toFixed(2)}</p>
                  </div>
                  <EvidenceMatchRing value={Math.round(citation.score * 100)} size={64} />
                </div>
              )}

              {citation.passage && (
                <div className="rounded-xl border border-border bg-card p-4">
                  <p className="text-[11px] tracking-[0.12em] text-muted-foreground uppercase">
                    Retrieved passage
                  </p>
                  <p className="mt-2 leading-relaxed">{citation.passage}</p>
                </div>
              )}
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}

function Field({ label, value, mono }: { label: string; value?: string | undefined; mono?: boolean }) {
  return (
    <div className="rounded-xl bg-muted/60 p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={mono ? "mt-1 font-mono text-sm break-all" : "mt-1 text-sm"}>{value ?? "—"}</p>
    </div>
  );
}
