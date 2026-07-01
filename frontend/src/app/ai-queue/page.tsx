import { DashboardShell } from "@/components/layout/dashboard-shell";

const stages = [
  ["Uploading", "done"],
  ["Transcribing", "done"],
  ["Finding highlights", "running"],
  ["Generating clips", "pending"],
  ["Applying style", "pending"],
  ["Ready for review", "pending"],
];

export default function AIQueuePage() {
  return (
    <DashboardShell title="AI Queue" actionHref="/review" actionLabel="Open Review">
      <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
        <p className="text-sm font-medium text-violet-300">Production in progress</p>
        <h2 className="mt-2 text-2xl font-semibold">Podcast bán hàng tự động</h2>
        <p className="mt-2 text-sm text-white/50">
          AI is processing the source video. This page replaces dashboard-style render widgets.
        </p>

        <div className="mt-8 space-y-3">
          {stages.map(([label, status]) => (
            <div key={label} className="flex items-center justify-between rounded-xl border border-white/10 bg-black/20 p-4">
              <div>
                <p className="font-medium">{label}</p>
                <p className="mt-1 text-sm text-white/40">{status}</p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs ${
                  status === "done"
                    ? "bg-emerald-400/15 text-emerald-200"
                    : status === "running"
                      ? "bg-violet-400/15 text-violet-200"
                      : "bg-white/10 text-white/45"
                }`}
              >
                {status}
              </span>
            </div>
          ))}
        </div>
      </section>
    </DashboardShell>
  );
}
