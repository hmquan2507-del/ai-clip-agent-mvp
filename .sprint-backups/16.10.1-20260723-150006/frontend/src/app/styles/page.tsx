import { DashboardShell } from "@/components/layout/dashboard-shell";

const styles = ["Talking Head", "Podcast", "Education", "Business", "Finance", "Real Estate"];

export default function StylesPage() {
  return (
    <DashboardShell title="Styles">
      <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
        <h2 className="text-2xl font-semibold">Production styles</h2>
        <p className="mt-2 text-sm text-white/50">
          Styles define subtitle, motion, B-roll, music, sound FX, and CTA behavior.
        </p>
        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {styles.map((style) => (
            <article key={style} className="rounded-2xl border border-white/10 bg-black/20 p-5">
              <p className="font-semibold">{style}</p>
              <p className="mt-2 text-sm text-white/45">Reusable AI production recipe</p>
              <button className="mt-5 rounded-xl bg-white/10 px-4 py-2 text-sm">Use style</button>
            </article>
          ))}
        </div>
      </section>
    </DashboardShell>
  );
}
