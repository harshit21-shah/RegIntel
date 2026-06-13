export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-indigo-600 shadow-glow">
        <svg viewBox="0 0 24 24" className="h-5 w-5 text-white" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 3L4 7v6c0 5 3.5 8.5 8 10 4.5-1.5 8-5 8-10V7l-8-4z" />
          <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
      {!compact && (
        <div>
          <p className="font-display text-base font-semibold tracking-tight text-slate-900 dark:text-white">RegIntel</p>
          <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">Compliance Intelligence</p>
        </div>
      )}
    </div>
  );
}
