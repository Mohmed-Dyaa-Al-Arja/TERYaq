import { useEffect, useRef, useState } from "react";
import { ArrowUp, Mic, Square } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export function ChatComposer({
  onSend,
  disabled,
  value,
  onValueChange,
}: {
  onSend: (question: string) => void;
  disabled?: boolean;
  value: string;
  onValueChange: (v: string) => void;
}) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (!disabled) ref.current?.focus();
  }, [disabled]);

  const submit = () => {
    const q = value.trim();
    if (!q || disabled) return;
    onSend(q);
    onValueChange("");
  };

  const toggleVoice = () => {
    const SR =
      (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition ?? null;
    if (!SR) {
      toast.error("Voice input is not supported in this browser.");
      return;
    }
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }
    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = false;
    rec.onresult = (e: any) => onValueChange(`${value} ${e.results[0][0].transcript}`.trim());
    rec.onerror = () => toast.error("Voice input failed. Please try again.");
    rec.onend = () => setListening(false);
    rec.start();
    recognitionRef.current = rec;
    setListening(true);
  };

  return (
    <div className="border-t border-border bg-background/90 px-4 py-4 backdrop-blur sm:px-8">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
        className="mx-auto max-w-4xl"
      >
        <label htmlFor="question" className="sr-only">
          Ask a clinical or educational question
        </label>
        <div className="flex items-end gap-2 rounded-2xl border border-border bg-card p-2 pl-4 shadow-card focus-within:border-teal/50">
          <textarea
            id="question"
            ref={ref}
            rows={1}
            value={value}
            disabled={disabled}
            onChange={(e) => {
              onValueChange(e.target.value);
              e.target.style.height = "auto";
              e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submit();
              }
            }}
            placeholder="Ask a clinical or educational question..."
            className="max-h-40 min-h-10 flex-1 resize-none bg-transparent py-2 text-[15px] outline-none placeholder:text-muted-foreground disabled:opacity-60"
          />
          <button
            type="button"
            onClick={toggleVoice}
            aria-label={listening ? "Stop voice input" : "Start voice input"}
            className={cn(
              "grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-border transition-colors hover:bg-muted",
              listening && "border-teal bg-teal-soft text-teal",
            )}
          >
            {listening ? <Square className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </button>
          <button
            type="submit"
            disabled={disabled || !value.trim()}
            aria-label="Send question"
            className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-40"
          >
            <ArrowUp className="h-4 w-4" />
          </button>
        </div>
        <p className="mt-3 text-center text-xs text-muted-foreground">
          Answers are generated from controlled clinical references only · Not medical advice
        </p>
      </form>
    </div>
  );
}
