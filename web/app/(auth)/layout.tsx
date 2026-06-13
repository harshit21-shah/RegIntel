import { Logo } from "@/components/Logo";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { CheckCircle2 } from "lucide-react";

const highlights = [
  "Clause-level diff detection across FDA, SEC, and state codes",
  "AI briefs with mandatory citations — no source, no claim",
  "Client-aware impact analysis via regulatory knowledge graph",
];

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-2">
      <div className="relative hidden overflow-hidden border-r border-slate-200 bg-slate-950 lg:flex lg:flex-col lg:justify-between lg:p-12 dark:border-white/[0.06]">
        <div className="absolute inset-0 mesh-gradient" />
        <div className="absolute -left-20 top-20 h-72 w-72 rounded-full bg-brand/10 blur-3xl" />
        <div className="relative">
          <Logo />
        </div>
        <div className="relative space-y-8">
          <h1 className="font-display text-4xl font-semibold leading-tight tracking-tight text-white">
            Regulatory change intelligence,
            <span className="text-gradient"> verified by source.</span>
          </h1>
          <ul className="space-y-4 text-sm text-slate-400">
            {highlights.map((item) => (
              <li key={item} className="flex gap-3">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-brand-glow" />
                {item}
              </li>
            ))}
          </ul>
        </div>
        <p className="relative text-xs text-slate-600">Enterprise-grade architecture · Citation-verified outputs</p>
      </div>

      <div className="relative flex min-h-screen flex-col">
        <div className="absolute right-6 top-6 z-10">
          <ThemeToggle compact />
        </div>
        <div className="flex flex-1 items-center justify-center px-6 py-12">
          <div className="w-full max-w-md">
            <div className="mb-8 lg:hidden">
              <Logo />
            </div>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
