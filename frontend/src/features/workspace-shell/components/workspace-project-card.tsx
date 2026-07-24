import Link from "next/link";
import { Clock3, Film, MoreHorizontal, Play } from "lucide-react";
import type { Production } from "@/lib/mock-productions";
import { statusLabel } from "@/lib/mock-productions";

export function WorkspaceProjectCard({ production }: { production: Production }) {
  return (
    <article className="group overflow-hidden rounded-2xl border border-white/[0.07] bg-[#12151c] transition hover:-translate-y-0.5 hover:border-white/[0.14] hover:bg-[#151922]">
      <Link href={`/editor/${production.id}`} className="relative block aspect-video overflow-hidden bg-[radial-gradient(circle_at_70%_20%,rgba(124,92,255,.28),transparent_35%),linear-gradient(145deg,#1c2130,#101218)]">
        <div className="absolute inset-0 grid place-items-center">
          <Film className="size-9 text-white/15" />
        </div>
        <span className="absolute bottom-3 right-3 rounded-md bg-black/55 px-2 py-1 text-[10px] font-medium text-white/75 backdrop-blur">{production.duration}</span>
        <span className="absolute inset-0 grid place-items-center bg-black/0 opacity-0 transition group-hover:bg-black/20 group-hover:opacity-100">
          <span className="grid size-10 place-items-center rounded-full bg-white text-black shadow-xl"><Play className="ml-0.5 size-4 fill-current" /></span>
        </span>
      </Link>

      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className="min-w-0 flex-1">
            <Link href={`/editor/${production.id}`} className="block truncate text-sm font-semibold text-white hover:text-violet-300">
              {production.title}
            </Link>
            <p className="mt-1 flex items-center gap-1.5 text-[11px] text-white/35">
              <Clock3 className="size-3" />
              {production.updatedAt}
            </p>
          </div>
          <button type="button" aria-label="Tùy chọn dự án" className="grid size-8 place-items-center rounded-lg text-white/30 transition hover:bg-white/[0.06] hover:text-white">
            <MoreHorizontal className="size-4" />
          </button>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <span className="rounded-full border border-white/[0.07] bg-white/[0.035] px-2.5 py-1 text-[10px] text-white/50">{statusLabel[production.status]}</span>
          <span className="text-[10px] text-white/30">{production.style}</span>
        </div>
      </div>
    </article>
  );
}
