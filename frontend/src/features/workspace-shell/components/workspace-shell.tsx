import type { ReactNode } from "react";
import { Bell, Menu, Search, Sparkles } from "lucide-react";
import { WorkspaceSidebar } from "./workspace-sidebar";

export function WorkspaceShell({ children }: { children: ReactNode }) {
  return (
    <main className="flex min-h-dvh bg-[#090b0f] text-white">
      <WorkspaceSidebar />
      <section className="min-w-0 flex-1">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-white/[0.06] bg-[#090b0f]/90 px-4 backdrop-blur-xl md:px-7">
          <button type="button" className="grid size-9 place-items-center rounded-xl text-white/60 hover:bg-white/[0.06] lg:hidden" aria-label="Mở menu"><Menu className="size-5" /></button>
          <div className="flex items-center gap-2 lg:hidden"><Sparkles className="size-4 text-violet-400" /><span className="text-sm font-semibold">AI Clip Agent</span></div>
          <label className="ml-auto hidden h-9 w-full max-w-sm items-center gap-2 rounded-xl border border-white/[0.07] bg-white/[0.035] px-3 md:flex">
            <Search className="size-4 text-white/30" />
            <input aria-label="Tìm dự án" placeholder="Tìm dự án..." className="min-w-0 flex-1 bg-transparent text-xs text-white outline-none placeholder:text-white/25" />
            <kbd className="rounded border border-white/[0.08] px-1.5 py-0.5 text-[9px] text-white/25">⌘ K</kbd>
          </label>
          <button type="button" className="relative grid size-9 place-items-center rounded-xl border border-white/[0.07] text-white/45 hover:bg-white/[0.05] hover:text-white" aria-label="Thông báo">
            <Bell className="size-4" /><span className="absolute right-2 top-2 size-1.5 rounded-full bg-violet-400" />
          </button>
        </header>
        {children}
      </section>
    </main>
  );
}
