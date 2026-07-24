import Link from "next/link";
import { ArrowRight, Clapperboard, Plus, Sparkles, Upload, WandSparkles } from "lucide-react";
import { WorkspaceProjectCard, WorkspaceShell } from "@/features/workspace-shell";
import { productions } from "@/lib/mock-productions";

export interface WorkspacePageProps {
  searchParams: Promise<{ intent?: string; view?: string }>;
}

export default async function WorkspacePage({ searchParams }: WorkspacePageProps) {
  const parameters = await searchParams;
  const showNewVideo = parameters.intent === "new";

  return (
    <WorkspaceShell>
      <div className="mx-auto w-full max-w-[1440px] px-4 py-8 md:px-7 md:py-10">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-medium text-violet-400">WORKSPACE</p>
            <h1 className="mt-2 text-2xl font-semibold tracking-tight md:text-3xl">Video của bạn</h1>
            <p className="mt-2 max-w-xl text-sm leading-6 text-white/40">Tạo video mới hoặc tiếp tục chỉnh sửa. Không có dashboard, không có bước trung gian.</p>
          </div>
          <Link href="/workspace?intent=new" className="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-white px-4 text-sm font-semibold text-[#111318] transition hover:bg-white/90">
            <Plus className="size-4" /> Video mới
          </Link>
        </div>

        <section className={`mt-8 overflow-hidden rounded-3xl border transition ${showNewVideo ? "border-violet-400/35 bg-violet-500/[0.07]" : "border-white/[0.07] bg-[#11141b]"}`}>
          <div className="grid lg:grid-cols-[1.1fr_.9fr]">
            <div className="p-6 md:p-8">
              <span className="inline-flex items-center gap-2 rounded-full border border-violet-400/20 bg-violet-500/10 px-3 py-1 text-[11px] font-medium text-violet-300"><Sparkles className="size-3" /> AI-FIRST CREATION</span>
              <h2 className="mt-5 max-w-xl text-2xl font-semibold leading-tight md:text-3xl">Bắt đầu một video, AI lo phần việc nặng.</h2>
              <p className="mt-3 max-w-xl text-sm leading-6 text-white/45">Tải video nguồn lên hoặc bắt đầu bằng ý tưởng. Sau đó bạn được đưa thẳng vào Editor để review, chỉnh timeline và export.</p>
              <div className="mt-6 flex flex-col gap-3 sm:flex-row">
                <Link href={`/editor/${productions[0]?.id ?? "new"}`} className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-violet-600 px-5 text-sm font-semibold text-white shadow-lg shadow-violet-950/30 transition hover:bg-violet-500"><Upload className="size-4" /> Tải video nguồn</Link>
                <Link href={`/editor/${productions[1]?.id ?? "new"}`} className="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-white/[0.1] bg-white/[0.04] px-5 text-sm font-medium text-white/75 transition hover:bg-white/[0.08] hover:text-white"><WandSparkles className="size-4" /> Bắt đầu bằng ý tưởng</Link>
              </div>
            </div>
            <div className="relative hidden min-h-[260px] overflow-hidden border-l border-white/[0.06] bg-[radial-gradient(circle_at_50%_25%,rgba(124,92,255,.22),transparent_32%),linear-gradient(145deg,#151a24,#0d0f15)] lg:block">
              <div className="absolute left-[12%] top-[17%] w-[76%] rounded-2xl border border-white/[0.09] bg-black/25 p-4 shadow-2xl backdrop-blur">
                <div className="aspect-video rounded-xl bg-gradient-to-br from-white/[0.08] to-transparent" />
                <div className="mt-3 flex gap-2"><div className="h-2 flex-1 rounded-full bg-violet-500/60"/><div className="h-2 w-1/4 rounded-full bg-cyan-400/40"/></div>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-10">
          <div className="flex items-center justify-between gap-4">
            <div><h2 className="text-lg font-semibold">Gần đây</h2><p className="mt-1 text-xs text-white/35">Mở lại và tiếp tục ngay trong Editor.</p></div>
            <button type="button" className="inline-flex items-center gap-1 text-xs text-white/45 hover:text-white">Xem tất cả <ArrowRight className="size-3.5" /></button>
          </div>
          <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
            {productions.map((production) => <WorkspaceProjectCard key={production.id} production={production} />)}
          </div>
        </section>

        <section className="mt-10 grid gap-4 md:grid-cols-3">
          {[{icon:Clapperboard,title:"Editor tập trung",text:"Preview, timeline, inspector và AI cùng một chỗ."},{icon:Sparkles,title:"AI xử lý nền",text:"Trạng thái xử lý hiển thị trong workflow, không cần trang Queue."},{icon:WandSparkles,title:"Export tại Editor",text:"Xuất video từ chính project đang làm, không đổi ngữ cảnh."}].map(({icon:Icon,title,text}) => (
            <div key={title} className="rounded-2xl border border-white/[0.06] bg-white/[0.025] p-5"><Icon className="size-5 text-violet-400"/><h3 className="mt-4 text-sm font-semibold">{title}</h3><p className="mt-2 text-xs leading-5 text-white/35">{text}</p></div>
          ))}
        </section>
      </div>
    </WorkspaceShell>
  );
}
