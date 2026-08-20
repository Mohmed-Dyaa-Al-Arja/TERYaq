import { useState, type ReactNode } from "react";
import { Menu } from "lucide-react";
import { AppSidebar } from "./AppSidebar";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";

export function AppShell({
  title,
  subtitle,
  action,
  children,
}: {
  title: string;
  subtitle: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="flex h-dvh w-full overflow-hidden bg-background">
      <aside className="hidden w-72 shrink-0 lg:block">
        <AppSidebar />
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 border-b border-border px-4 py-4 sm:px-8">
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger
              aria-label="Open navigation"
              className="grid h-10 w-10 place-items-center rounded-xl border border-border lg:hidden"
            >
              <Menu className="h-4 w-4" />
            </SheetTrigger>
            <SheetContent side="left" className="w-72 bg-sidebar p-0">
              <SheetTitle className="sr-only">Navigation</SheetTitle>
              <AppSidebar onNavigate={() => setOpen(false)} />
            </SheetContent>
          </Sheet>
          <div className="min-w-0 lg:col-start-2">
            <h1 className="truncate font-display text-xl font-bold tracking-tight sm:text-2xl">
              {title}
            </h1>
            <p className="truncate text-sm text-muted-foreground">{subtitle}</p>
          </div>
          <div className="shrink-0">{action}</div>
        </header>

        {children}
      </div>
    </div>
  );
}
