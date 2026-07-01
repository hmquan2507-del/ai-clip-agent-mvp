import { DashboardShell } from "@/components/layout/dashboard-shell";
import Link from "next/link";

const activeProductions = [
  { name: "Podcast bán hàng tự động", status: "Ready for review", clips: "8 clips" },
  { name: "Livestream mỹ phẩm", status: "AI queue", clips: "Processing" },
  { name: "Business talk", status: "Export ready", clips: "4 clips" },
];

export default function Home() {
  return (
    <DashboardShell title="Home" actionHref="/upload" actionLabel="Start Production">
      <div className="mb-8">
        <p className="text-sm font-medium text-violet-300">AI video production</p>
        <h2 className="mt-2 max-w-3xl text-3xl font-bold tracking-tight">
          Upload once. AI edits everything. Review. Export.
        </h2>
        <p className="mt-3 max-w-2xl text-white/50">
          Start a production or continue reviewing AI-generated clips. Home stays
          focused on production flow, not admin dashboard clutter.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {[
          ["Active productions", "3"],
          ["Ready to review", "1"],
          ["In AI queue", "1"],
          ["Export ready", "1"],
        ].map(([label, value]) => (
          <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <p className="text-sm text-white/50">{label}</p>
            <p className="mt-3 text-3xl font-bold">{value}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex items-center justify-between gap-4">
            <h3 className="text-lg font-semibold">Recent productions</h3>
            <Link href="/productions" className="text-sm text-violet-300 hover:text-violet-200">
              View all
            </Link>
          </div>
          <div className="mt-5 space-y-3">
            {activeProductions.map((production) => (
              <div key={production.name} className="flex items-center justify-between gap-4 rounded-xl bg-white/5 p-4">
                <div>
                  <p className="font-medium">{production.name}</p>
                  <p className="text-sm text-white/40">{production.status} · {production.clips}</p>
                </div>
                <Link href="/review" className="rounded-lg bg-white/10 px-3 py-2 text-sm hover:bg-white/15">
                  Open
                </Link>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-violet-400/20 bg-violet-600/15 p-6">
          <h3 className="text-lg font-semibold">Next step</h3>
          <p className="mt-3 text-sm text-white/60">
            Create a production and let AI move it through upload, queue, review,
            and export.
          </p>
          <Link
            href="/upload"
            className="mt-6 block w-full rounded-xl bg-white px-4 py-3 text-center text-sm font-semibold text-black"
          >
            Start Production
          </Link>
        </div>
      </div>
    </DashboardShell>
  );
}
