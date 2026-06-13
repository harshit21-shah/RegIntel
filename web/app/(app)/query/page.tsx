"use client";

import { useQuery } from "@tanstack/react-query";
import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import { MessageSquare, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-keys";
import { useAppStore } from "@/stores/app-store";
import { ChatMessage, TypingIndicator, type ChatMessageData } from "@/components/features/chat-message";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, Textarea } from "@/components/ui/input";

const SUGGESTED = [
  "What are SEC filings?",
  "What is EDGAR?",
  "What is the FDA and what does it regulate?",
  "What are principal display panel requirements under 21 CFR 101?",
];

export default function QueryPage() {
  const [question, setQuestion] = useState("");
  const { activeClientId, setActiveClientId } = useAppStore();
  const clientId = activeClientId ?? "";
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const { data: profiles } = useQuery({
    queryKey: queryKeys.profiles(1),
    queryFn: () => api.profiles.list(1, 100),
  });

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function ask(text: string) {
    const trimmed = text.trim();
    if (trimmed.length < 3) {
      toast.error("Question must be at least 3 characters.");
      return;
    }
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setQuestion("");
    try {
      const data = await api.query.ask(trimmed, clientId || null);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          citations: data.citations,
          status: data.status,
          confidence: data.confidence,
        },
      ]);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Query failed");
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!loading) void ask(question);
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (!loading && question.trim()) void ask(question);
    }
  }

  return (
    <div className="flex h-[calc(100vh-7rem)] flex-col lg:h-[calc(100vh-5.5rem)]">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="heading-display">Compliance Query</h1>
          <p className="mt-2 text-muted max-w-2xl">
            Citation-backed answers from your indexed regulatory corpus. Enter to send, Shift+Enter for new line.
          </p>
        </div>
        <div className="w-full sm:w-56">
          <Label htmlFor="client" className="text-[10px]">
            Client context
          </Label>
          <Select
            id="client"
            value={clientId}
            onChange={(e) => setActiveClientId(e.target.value || null)}
            className="mt-1.5"
          >
            <option value="">All clients</option>
            {(profiles?.items ?? []).map((p) => (
              <option key={p.client_id} value={p.client_id}>
                {p.name}
              </option>
            ))}
          </Select>
        </div>
      </div>

      <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-3xl border border-slate-200/80 bg-white/50 dark:border-white/[0.08] dark:bg-surface-raised/40">
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center px-4 text-center">
              <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl border border-brand/25 bg-gradient-to-br from-brand/15 to-indigo-500/10 shadow-glow">
                <Sparkles className="h-8 w-8 text-brand-glow" />
              </div>
              <h2 className="font-display text-xl font-semibold text-slate-900 dark:text-white">
                Ask anything about your indexed regulations
              </h2>
              <p className="mt-2 max-w-md text-sm text-muted">
                Every factual claim must link to a source clause. Unverified answers are flagged explicitly.
              </p>
              <div className="mt-8 grid w-full max-w-lg gap-2 sm:grid-cols-2">
                {SUGGESTED.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    onClick={() => ask(prompt)}
                    disabled={loading}
                    className="group rounded-xl border border-slate-200/80 bg-white px-3 py-3 text-left text-xs leading-relaxed text-slate-600 transition hover:border-brand/40 hover:bg-brand/5 hover:text-slate-900 disabled:opacity-50 dark:border-white/[0.08] dark:bg-surface/60 dark:text-slate-400 dark:hover:text-white"
                  >
                    <MessageSquare className="mb-2 h-3.5 w-3.5 text-slate-400 group-hover:text-brand-glow" />
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="mx-auto max-w-3xl space-y-6">
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              {loading && <TypingIndicator />}
            </div>
          )}
        </div>

        <form
          onSubmit={onSubmit}
          className="border-t border-slate-200/80 bg-white/80 p-4 backdrop-blur-xl dark:border-white/[0.06] dark:bg-surface/80 sm:p-5"
        >
          <div className="mx-auto flex max-w-3xl gap-3">
            <Textarea
              ref={inputRef}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Ask about SEC filings, FDA labeling, compliance obligations…"
              rows={2}
              className="min-h-[52px] resize-none"
              disabled={loading}
            />
            <Button type="submit" size="lg" className="shrink-0 self-end" disabled={loading || !question.trim()}>
              {loading ? "…" : "Send"}
            </Button>
          </div>
          <p className="mx-auto mt-2 max-w-3xl text-center text-[11px] text-muted">
            Not legal advice · Every claim requires a verifiable source citation
          </p>
        </form>
      </div>
    </div>
  );
}
