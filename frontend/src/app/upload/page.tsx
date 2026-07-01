import { DashboardShell } from "@/components/layout/dashboard-shell";

export default function UploadPage() {
  return (
    <DashboardShell title="Upload" actionHref="/ai-queue" actionLabel="View AI Queue">
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <p className="text-sm font-medium text-violet-300">New production</p>
          <h2 className="mt-2 text-2xl font-semibold">Upload source video</h2>
          <p className="mt-2 text-sm text-white/50">
            Add one source video, choose a style, then send it to the AI queue.
          </p>

          <div className="mt-6 rounded-2xl border border-dashed border-white/20 bg-black/20 p-10 text-center">
            <p className="text-lg font-semibold">Drop video here</p>
            <p className="mt-2 text-sm text-white/45">MP4, MOV, AVI, MKV</p>
            <button className="mt-5 rounded-xl bg-violet-600 px-5 py-3 text-sm font-medium hover:bg-violet-500">
              Choose File
            </button>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <label className="space-y-2 text-sm text-white/60">
              Production title
              <input
                className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-violet-400"
                placeholder="Podcast bán hàng tự động"
              />
            </label>
            <label className="space-y-2 text-sm text-white/60">
              Style
              <select className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-violet-400">
                <option>Talking Head</option>
                <option>Podcast</option>
                <option>Education</option>
                <option>Business</option>
              </select>
            </label>
            <label className="space-y-2 text-sm text-white/60 md:col-span-2">
              Objective
              <textarea
                className="min-h-28 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-violet-400"
                placeholder="Tạo clip ngắn để kéo inbox tư vấn"
              />
            </label>
          </div>
        </section>

        <aside className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-lg font-semibold">After upload</h3>
          <div className="mt-5 space-y-4 text-sm text-white/55">
            {["Validate file", "Extract metadata", "Start transcript", "Move to AI queue"].map((step) => (
              <div key={step} className="rounded-xl bg-white/5 p-4">{step}</div>
            ))}
          </div>
        </aside>
      </div>
    </DashboardShell>
  );
}
