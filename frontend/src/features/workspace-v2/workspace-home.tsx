import Link from "next/link";
import { ArrowRight, Clock3, Film, FolderOpen, Plus, Sparkles } from "lucide-react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { productions, statusLabel, statusTone } from "@/lib/mock-productions";

const DEFAULT_PRODUCTION_ID = "221e4b01-5fb9-4b4a-a549-4fb32c455059";

function editorHref(index: number) {
  return index === 0
    ? `/editor/${DEFAULT_PRODUCTION_ID}`
    : `/editor/${encodeURIComponent(productions[index].id)}`;
}

export function WorkspaceHome() {
  return (
    <DashboardShell
      title="Workspace"
      eyebrow="AI Clip Agent"
      actionHref="/upload"
      actionLabel="New video"
    >
      <div className="mx-auto grid max-w-7xl gap-7">
        <section className="overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-violet-950/70 via-slate-950 to-slate-950 p-6 md:p-8">
          <div className="grid items-end gap-8 lg:grid-cols-[1fr_auto]">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1 text-xs text-violet-200">
                <Sparkles className="h-3.5 w-3.5" />
                AI-first video production
              </div>
              <h2 className="mt-5 max-w-3xl text-3xl font-semibold tracking-tight md:text-4xl">
                Create, continue and finish videos from one workspace.
              </h2>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-white/55">
                Workspace is now the canonical product home. Existing Upload,
                Review, Export and Queue routes remain available while the new
                information architecture is introduced safely.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link
                href="/upload"
                className="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-medium hover:bg-violet-500"
              >
                <Plus className="h-4 w-4" /> New video
              </Link>
              <Link
                href={`/editor/${DEFAULT_PRODUCTION_ID}`}
                className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium hover:bg-white/10"
              >
                Continue editing <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          {[
            { label: "Recent projects", value: productions.length, icon: FolderOpen },
            { label: "Ready to review", value: productions.filter((item) => item.status === "review_ready").length, icon: Film },
            { label: "Processing", value: productions.filter((item) => item.status === "processing").length, icon: Sparkles },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <article key={item.label} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-white/50">{item.label}</p>
                  <Icon className="h-4 w-4 text-violet-300" />
                </div>
                <p className="mt-3 text-3xl font-semibold">{item.value}</p>
              </article>
            );
          })}
        </section>

        <section>
          <div className="mb-4 flex items-end justify-between gap-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.2em] text-violet-300">Projects</p>
              <h3 className="mt-2 text-2xl font-semibold">Recent videos</h3>
            </div>
            <Link href="/productions" className="text-sm text-white/55 hover:text-white">
              Legacy productions
            </Link>
          </div>

          <div className="grid gap-4">
            {productions.map((production, index) => (
              <article key={production.id} className="group rounded-2xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-violet-400/30 hover:bg-white/[0.05]">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                  <div className="flex h-20 w-full shrink-0 items-center justify-center rounded-xl bg-black/30 text-white/35 sm:w-32">
                    <Film className="h-7 w-7" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge tone={statusTone[production.status]}>{statusLabel[production.status]}</Badge>
                      <Badge>{production.style}</Badge>
                    </div>
                    <h4 className="mt-3 truncate font-semibold">{production.title}</h4>
                    <p className="mt-1 line-clamp-1 text-sm text-white/45">{production.description}</p>
                    <div className="mt-3 flex items-center gap-3 text-xs text-white/35">
                      <span className="inline-flex items-center gap-1"><Clock3 className="h-3.5 w-3.5" />{production.updatedAt}</span>
                      <span>{production.duration}</span>
                    </div>
                  </div>
                  <Link
                    href={editorHref(index)}
                    className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-white/10 px-4 py-2.5 text-sm font-medium transition group-hover:border-violet-400/30 group-hover:bg-violet-500/10"
                  >
                    Open editor <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </DashboardShell>
  );
}
