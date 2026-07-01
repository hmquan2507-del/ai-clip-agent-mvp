import { DashboardShell } from "@/components/layout/dashboard-shell";

export default function SettingsPage() {
  return (
    <DashboardShell title="Settings">
      <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
        <h2 className="text-2xl font-semibold">Workspace settings</h2>
        <p className="mt-2 text-sm text-white/50">
          Provider, storage, credits, and workspace settings stay separate from production flow.
        </p>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {["AI Providers", "Storage", "Credits", "Workspace"].map((name) => (
            <div key={name} className="rounded-2xl border border-white/10 bg-black/20 p-5">
              <p className="font-semibold">{name}</p>
              <p className="mt-2 text-sm text-white/45">Configuration placeholder</p>
            </div>
          ))}
        </div>
      </section>
    </DashboardShell>
  );
}
