import { DashboardShell } from "@/components/layout/dashboard-shell";

const stats = [
  { label: "Videos uploaded", value: "12" },
  { label: "Clips generated", value: "48" },
  { label: "Rendering", value: "3" },
  { label: "Failed renders", value: "1" },
];

export default function Home() {
  return (
    <DashboardShell>
      <div className="mb-8">
        <h2 className="text-3xl font-bold tracking-tight">Welcome back, Quân 👋</h2>
        <p className="mt-2 text-white/50">
          Manage videos, AI suggestions, clips, and render jobs in one workspace.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <p className="text-sm text-white/50">{stat.label}</p>
            <p className="mt-3 text-3xl font-bold">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-lg font-semibold">Recent Projects</h3>
          <div className="mt-5 space-y-3">
            {["podcast-demo.mp4", "interview-marketing.mp4", "business-talk.mp4"].map((name) => (
              <div key={name} className="flex items-center justify-between rounded-xl bg-white/5 p-4">
                <div>
                  <p className="font-medium">{name}</p>
                  <p className="text-sm text-white/40">AI found 8 potential clips</p>
                </div>
                <button className="rounded-lg bg-violet-600 px-3 py-2 text-sm">Open</button>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-violet-600/20 to-blue-600/10 p-6">
          <h3 className="text-lg font-semibold">AI Studio</h3>
          <p className="mt-3 text-sm text-white/60">
            Generate hooks, captions, CTAs, hashtags, and viral clips from your source videos.
          </p>
          <button className="mt-6 w-full rounded-xl bg-white px-4 py-3 text-sm font-semibold text-black">
            Start AI Analysis
          </button>
        </div>
      </div>
    </DashboardShell>
  );
}
