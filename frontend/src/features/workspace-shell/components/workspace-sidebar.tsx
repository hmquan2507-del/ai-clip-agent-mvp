import Link from "next/link";
import {
  Boxes,
  ChevronDown,
  Clock3,
  FolderOpen,
  Library,
  Plus,
  Settings,
  Sparkles,
} from "lucide-react";

const primaryItems = [
  { label: "Dự án", href: "/workspace", icon: FolderOpen },
  { label: "Tài nguyên", href: "/workspace?view=assets", icon: Library },
  { label: "Mẫu video", href: "/workspace?view=templates", icon: Boxes },
];

export function WorkspaceSidebar() {
  return (
    <aside className="hidden h-dvh w-[248px] shrink-0 flex-col border-r border-white/[0.07] bg-[#0b0d12] p-3 lg:flex">
      <div className="flex h-12 items-center gap-2.5 px-2">
        <span className="grid size-8 place-items-center rounded-xl bg-violet-600 shadow-lg shadow-violet-950/40">
          <Sparkles className="size-4 text-white" />
        </span>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-white">AI Clip Agent</p>
          <p className="text-[11px] text-white/35">Video workspace</p>
        </div>
      </div>

      <Link
        href="/workspace?intent=new"
        className="mt-3 flex h-10 items-center justify-center gap-2 rounded-xl bg-white text-sm font-semibold text-[#111318] transition hover:bg-white/90"
      >
        <Plus className="size-4" />
        Video mới
      </Link>

      <nav className="mt-5 space-y-1" aria-label="Workspace">
        {primaryItems.map((item, index) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.label}
              href={item.href}
              className={`flex h-10 items-center gap-3 rounded-xl px-3 text-sm transition ${
                index === 0
                  ? "bg-white/[0.08] text-white"
                  : "text-white/55 hover:bg-white/[0.05] hover:text-white"
              }`}
            >
              <Icon className="size-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-6 px-3">
        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-white/25">
          Gần đây
        </p>
        <div className="mt-3 space-y-2 text-xs text-white/45">
          <p className="flex items-center gap-2 truncate"><Clock3 className="size-3.5" />Podcast bán hàng</p>
          <p className="flex items-center gap-2 truncate"><Clock3 className="size-3.5" />AI education short</p>
        </div>
      </div>

      <div className="mt-auto space-y-2">
        <div className="rounded-xl border border-white/[0.07] bg-white/[0.035] p-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-white/45">Dung lượng</span>
            <span className="text-white/70">2.4 / 10 GB</span>
          </div>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/[0.08]">
            <div className="h-full w-[24%] rounded-full bg-violet-500" />
          </div>
        </div>

        <Link href="/settings" className="flex h-10 items-center gap-3 rounded-xl px-3 text-sm text-white/50 transition hover:bg-white/[0.05] hover:text-white">
          <Settings className="size-4" />
          Cài đặt
        </Link>

        <button type="button" className="flex w-full items-center gap-3 rounded-xl border border-white/[0.07] p-2 text-left">
          <span className="grid size-8 place-items-center rounded-lg bg-violet-500/20 text-xs font-semibold text-violet-200">HQ</span>
          <span className="min-w-0 flex-1">
            <span className="block truncate text-xs font-medium text-white">Hồ Quân</span>
            <span className="block truncate text-[10px] text-white/35">Cá nhân</span>
          </span>
          <ChevronDown className="size-3.5 text-white/30" />
        </button>
      </div>
    </aside>
  );
}
