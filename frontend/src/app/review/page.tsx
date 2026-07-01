import { DashboardShell } from "@/components/layout/dashboard-shell";

const clips = [
  "Sai lầm khiến video không ra đơn",
  "Cách biến livestream thành 10 clip",
  "Hook đầu video quyết định 3 giây đầu",
];

export default function ReviewPage() {
  return (
    <DashboardShell title="Review" actionHref="/export" actionLabel="Export Approved">
      <div className="grid gap-6 xl:grid-cols-[0.75fr_1.25fr_0.9fr]">
        <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <h2 className="text-lg font-semibold">Generated clips</h2>
          <div className="mt-4 space-y-3">
            {clips.map((clip, index) => (
              <button
                key={clip}
                className={`w-full rounded-xl p-4 text-left text-sm ${
                  index === 0 ? "bg-violet-600 text-white" : "bg-white/5 text-white/65"
                }`}
              >
                <p className="font-medium">{clip}</p>
                <p className="mt-1 text-xs opacity-70">AI score {92 - index * 6}</p>
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <div className="flex aspect-[9/16] max-h-[620px] items-center justify-center rounded-2xl bg-black/50">
            <div className="px-8 text-center">
              <p className="text-sm text-violet-300">Preview</p>
              <h3 className="mt-3 text-2xl font-bold">Sai lầm khiến video không ra đơn</h3>
              <p className="mt-3 text-white/50">AI-generated review preview</p>
            </div>
          </div>
        </section>

        <aside className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <h2 className="text-lg font-semibold">AI plan</h2>
          <div className="mt-4 space-y-4 text-sm">
            <div className="rounded-xl bg-white/5 p-4">
              <p className="text-white/45">Reason</p>
              <p className="mt-2">Strong pain point and clear business outcome.</p>
            </div>
            <div className="rounded-xl bg-white/5 p-4">
              <p className="text-white/45">CTA</p>
              <p className="mt-2">Nhắn tin để em gửi checklist tối ưu clip.</p>
            </div>
          </div>
          <div className="mt-6 grid gap-3">
            <button className="rounded-xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-black">
              Approve
            </button>
            <button className="rounded-xl bg-white/10 px-4 py-3 text-sm font-semibold">
              Regenerate
            </button>
            <button className="rounded-xl bg-white/5 px-4 py-3 text-sm text-white/70">
              Reject
            </button>
          </div>
        </aside>
      </div>
    </DashboardShell>
  );
}
