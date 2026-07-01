import { DashboardShell } from "@/components/layout/dashboard-shell";

export default function ProductionsPage() {
  return (
    <DashboardShell title="Productions">
      <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
        <h2 className="text-2xl font-semibold">All productions</h2>
        <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
          {["Podcast bán hàng tự động", "Livestream mỹ phẩm", "Business talk"].map((name) => (
            <div key={name} className="flex items-center justify-between border-b border-white/10 p-4 last:border-b-0">
              <div>
                <p className="font-medium">{name}</p>
                <p className="text-sm text-white/40">AI production workflow</p>
              </div>
              <button className="rounded-lg bg-white/10 px-3 py-2 text-sm">Open</button>
            </div>
          ))}
        </div>
      </section>
    </DashboardShell>
  );
}
