import { cn } from "@/lib/utils";
import type { EvidenceStatus } from "@/lib/types";

const styles: Record<EvidenceStatus, string> = {
  Strong: "bg-teal-soft text-teal",
  Moderate: "bg-accent text-accent-foreground",
  Limited: "bg-secondary text-secondary-foreground",
  Insufficient: "bg-destructive/10 text-destructive",
};

export function EvidenceBadge({
  status,
  className,
}: {
  status: EvidenceStatus;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium",
        styles[status],
        className,
      )}
    >
      <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-current" aria-hidden />
      {status} evidence
    </span>
  );
}

export function EvidenceMatchRing({ value, size = 76 }: { value: number; size?: number }) {
  const stroke = 6;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, value));

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      role="img"
      aria-label={`Evidence match ${pct} percent`}
      className="shrink-0"
    >
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        strokeWidth={stroke}
        className="stroke-teal-soft"
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={`${(pct / 100) * c} ${c}`}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        className="stroke-teal transition-[stroke-dasharray] duration-700"
      />
      <text
        x="50%"
        y="50%"
        dominantBaseline="central"
        textAnchor="middle"
        className="fill-foreground text-[15px] font-semibold"
      >
        {pct}%
      </text>
    </svg>
  );
}
