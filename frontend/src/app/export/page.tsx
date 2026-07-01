import { DashboardShell } from "@/components/layout/dashboard-shell";

export default function ExportPage() {
  return (
    <DashboardShell title="Export" actionHref="/upload" actionLabel="New Production">
      <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
        <h2 className="text-2xl font-semibold">Approved clips</h2>
        <p className="mt-2 text-sm text-white/50">
          Render approved clips and download social-ready outputs.
        </p>

        <div className="mt-6 grid gap-4 lg:grid-cols-3">
          {["Clip 01", "Clip 02", "Clip 03"].map((clip, index) => (
            <article key={clip} className="rounded-2xl border border-white/10 bg-black/20 p-5">
              <p className="font-semibold">{clip}</p>
              <p className="mt-2 text-sm text-white/45">1080x1920 MP4</p>
              <p className="mt-4 text-sm text-emerald-200">{index === 0 ? "Ready" : "Waiting render"}</p>
              <button className="mt-5 w-full rounded-xl bg-white px-4 py-3 text-sm font-semibold text-black">
                {index === 0 ? "Download" : "Render"}
              </button>
            </article>
          ))}
        </div>
      </section>
    </DashboardShell>
  );
}
