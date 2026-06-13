"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, CheckCircle2, Shield, Sparkles, Zap } from "lucide-react";
import { Logo } from "@/components/Logo";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: Zap,
    title: "Clause-level detection",
    body: "Track FDA, SEC, EPA, and state code diffs with severity scoring — not document-level noise.",
  },
  {
    icon: Shield,
    title: "Citation-backed briefs",
    body: "Every claim links to a verbatim source clause. No citation, no claim.",
  },
  {
    icon: Sparkles,
    title: "GraphRAG retrieval",
    body: "Hybrid vector + graph search with reranking for client-aware regulatory context.",
  },
  {
    icon: CheckCircle2,
    title: "Verified pipeline",
    body: "Multi-agent synthesis with a verification gate before any brief is delivered.",
  },
];

const sampleQueries = ["What is the FDA?", "What are SEC filings?", "What is EDGAR?"];

const stats = [
  { label: "Sources indexed", value: "FDA · SEC · eCFR" },
  { label: "Citation policy", value: "Mandatory" },
  { label: "Verification", value: "Multi-agent" },
];

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.5, ease: [0.22, 1, 0.36, 1] },
  }),
};

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden app-grid-bg">
      <div className="pointer-events-none absolute inset-0 mesh-gradient" />
      <div className="pointer-events-none absolute -right-32 top-1/3 h-96 w-96 rounded-full bg-indigo-500/10 blur-3xl" />

      <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <Logo />
        <div className="flex items-center gap-2">
          <ThemeToggle compact />
          <Link href="/login" className="no-underline">
            <Button variant="ghost" size="sm">
              Sign in
            </Button>
          </Link>
          <Link href="/register" className="no-underline">
            <Button size="sm">
              Get started
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-6xl px-6 pb-24 pt-4">
        <motion.section initial="hidden" animate="visible" className="mx-auto max-w-3xl text-center">
          <motion.p
            custom={0}
            variants={fadeUp}
            className="mb-4 inline-flex items-center gap-2 rounded-full border border-brand/25 bg-brand/10 px-3 py-1 text-xs font-medium uppercase tracking-wider text-brand dark:text-brand-glow"
          >
            <Sparkles className="h-3 w-3" />
            Regulatory change intelligence
          </motion.p>
          <motion.h1
            custom={1}
            variants={fadeUp}
            className="font-display text-4xl font-semibold tracking-tight text-slate-900 dark:text-white sm:text-5xl lg:text-6xl"
          >
            Know what changed.
            <span className="block text-gradient">Prove every answer.</span>
          </motion.h1>
          <motion.p
            custom={2}
            variants={fadeUp}
            className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-muted"
          >
            RegIntel ingests regulatory sources, detects clause-level changes, and generates verified
            compliance briefs with mandatory citations.
          </motion.p>
          <motion.div
            custom={3}
            variants={fadeUp}
            className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row"
          >
            <Link href="/login" className="no-underline">
              <Button size="lg">
                Open workspace
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/login" className="no-underline">
              <Button variant="secondary" size="lg">
                Request demo
              </Button>
            </Link>
          </motion.div>
        </motion.section>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="mx-auto mt-16 flex max-w-2xl flex-wrap items-center justify-center gap-6 rounded-2xl border border-slate-200/80 bg-white/60 px-6 py-4 backdrop-blur dark:border-white/[0.08] dark:bg-surface-raised/50"
        >
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-[10px] font-medium uppercase tracking-wider text-muted">{stat.label}</p>
              <p className="mt-1 text-sm font-medium text-slate-900 dark:text-white">{stat.value}</p>
            </div>
          ))}
        </motion.div>

        <section className="mt-24 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.06, duration: 0.4 }}
              >
                <Card className="h-full transition duration-300 hover:-translate-y-0.5 hover:border-brand/25 hover:shadow-glow">
                  <CardHeader>
                    <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-brand/10 text-brand dark:text-brand-glow">
                      <Icon className="h-5 w-5" />
                    </div>
                    <CardTitle className="text-base text-slate-900 dark:text-white">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="leading-relaxed">{feature.body}</CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </section>

        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mt-24"
        >
          <Card className="overflow-hidden border-brand/20 bg-gradient-to-br from-brand/5 via-transparent to-indigo-500/5 p-8 lg:p-10">
            <div className="grid gap-8 lg:grid-cols-2 lg:items-center">
              <div>
                <h2 className="font-display text-2xl font-semibold text-slate-900 dark:text-white">
                  Ask a question. Get cited answers.
                </h2>
                <p className="mt-3 text-sm leading-relaxed text-muted">
                  The query engine searches indexed FDA, SEC, and reference glossary clauses.
                </p>
                <ul className="mt-6 space-y-2">
                  {sampleQueries.map((q) => (
                    <li
                      key={q}
                      className="rounded-xl border border-slate-200/80 bg-white/80 px-4 py-2.5 text-sm text-slate-700 dark:border-white/[0.06] dark:bg-surface-overlay dark:text-slate-300"
                    >
                      &ldquo;{q}&rdquo;
                    </li>
                  ))}
                </ul>
              </div>
              <div className="rounded-2xl border border-slate-200/80 bg-slate-900 p-6 font-mono text-xs leading-relaxed shadow-glow dark:border-white/[0.08]">
                <p className="text-brand-glow">Query → Retrieval → Synthesis → Verification</p>
                <p className="mt-4 text-slate-500">
                  status: <span className="text-emerald-400">COMPLETE</span>
                  <span className="ml-3 text-slate-600">confidence: 98%</span>
                </p>
                <p className="mt-3 text-slate-200">
                  The FDA is responsible for protecting public health by assuring the safety, efficacy,
                  and security of drugs, devices, and the food supply…
                </p>
                <p className="mt-4 border-t border-white/10 pt-4 text-slate-500">
                  [ref:fda:glossary:overview] · fda.gov
                </p>
              </div>
            </div>
          </Card>
        </motion.section>
      </main>

      <footer className="relative z-10 border-t border-slate-200/80 py-8 text-center text-xs text-muted dark:border-white/[0.06]">
        RegIntel — GraphRAG compliance intelligence. Not legal advice.
      </footer>
    </div>
  );
}
