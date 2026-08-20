import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { Bookmark, Clock, MessageSquareText, Moon, Plus, Sun } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/lib/theme";
import { useStore } from "@/lib/store";
import logoAsset from "@/assets/teryaq-logo.jpg.asset.json";

const nav = [
  { to: "/", label: "Chat", icon: MessageSquareText },
  { to: "/history", label: "History", icon: Clock },
  { to: "/saved", label: "Saved Evidence", icon: Bookmark },
] as const;

export function AppSidebar({ onNavigate }: { onNavigate?: () => void }) {
  const path = useRouterState({ select: (r) => r.location.pathname });
  const { theme, toggle } = useTheme();
  const { conversations, createConversation } = useStore();
  const navigate = useNavigate();

  return (
    <nav
      aria-label="Main"
      className="flex h-full w-full flex-col bg-sidebar text-sidebar-foreground"
    >
      <div className="px-6 pt-7 pb-6">
        <div className="flex items-center gap-3">
          <img
            src={logoAsset.url}
            alt="TERYAQ"
            className="h-9 w-9 shrink-0 rounded-lg object-cover"
          />
          <span className="font-display text-xl font-bold tracking-tight">TERYAQ</span>
        </div>
        <p className="mt-3 text-[11px] tracking-[0.14em] text-navy-muted uppercase">
          Clinical Evidence Assistant
        </p>
      </div>

      <div className="px-4">
        <button
          type="button"
          onClick={() => {
            createConversation();
            onNavigate?.();
            navigate({ to: "/" });
          }}
          className="flex w-full items-center gap-2 rounded-xl border border-sidebar-border px-4 py-3 text-sm font-medium transition-colors hover:bg-sidebar-accent"
        >
          <Plus className="h-4 w-4 shrink-0" aria-hidden />
          New Conversation
        </button>
      </div>

      <ul className="mt-4 space-y-1 px-4">
        {nav.map(({ to, label, icon: Icon }) => {
          const active = path === to;
          return (
            <li key={to}>
              <Link
                to={to}
                onClick={onNavigate}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-4 py-3 text-sm transition-colors",
                  active
                    ? "bg-sidebar-accent font-medium text-sidebar-accent-foreground"
                    : "text-navy-muted hover:bg-sidebar-accent/60 hover:text-sidebar-foreground",
                )}
              >
                <Icon className="h-4 w-4 shrink-0" aria-hidden />
                <span className="min-w-0 flex-1 truncate">{label}</span>
                {to === "/" && conversations.length > 0 && (
                  <span className="rounded-md bg-sidebar-border px-1.5 text-xs">
                    {conversations.length}
                  </span>
                )}
              </Link>
            </li>
          );
        })}
      </ul>

      <div className="mt-auto space-y-4 px-6 pt-6 pb-7">
        <button
          type="button"
          onClick={toggle}
          role="switch"
          aria-checked={theme === "dark"}
          aria-label="Toggle dark mode"
          className="flex items-center gap-2 rounded-full border border-sidebar-border px-3 py-2"
        >
          <Sun className="h-3.5 w-3.5 text-navy-muted" aria-hidden />
          <span className="relative h-4 w-8 rounded-full bg-sidebar-border">
            <span
              className={cn(
                "absolute top-0.5 h-3 w-3 rounded-full bg-sidebar-foreground transition-all",
                theme === "dark" ? "left-4 bg-teal" : "left-0.5",
              )}
            />
          </span>
          <Moon className="h-3.5 w-3.5 text-navy-muted" aria-hidden />
        </button>

        <ul className="space-y-1.5 text-xs text-navy-muted">
          {["Evidence-grounded", "Source-traceable", "Reference-backed"].map((t) => (
            <li key={t} className="flex items-center gap-2">
              <span className="h-1 w-1 rounded-full bg-teal" aria-hidden />
              {t}
            </li>
          ))}
        </ul>

        <p className="text-[11px] leading-relaxed text-navy-muted/70">
          Educational information only — not a diagnosis or medical advice.
        </p>
      </div>
    </nav>
  );
}
