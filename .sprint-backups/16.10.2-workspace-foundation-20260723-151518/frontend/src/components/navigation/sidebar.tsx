"use client";

import {
  CheckCircle2,
  Film,
  FolderKanban,
  Home,
  ListChecks,
  Layers,
  Settings,
  Sparkles,
  Upload,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  { label: "Home", href: "/", icon: Home },
  { label: "Upload", href: "/upload", icon: Upload },
  { label: "AI Queue", href: "/ai-queue", icon: ListChecks },
  { label: "Review", href: "/review", icon: CheckCircle2 },
  { label: "Export", href: "/export", icon: Film },
  { label: "Productions", href: "/productions", icon: FolderKanban },
  { label: "Styles", href: "/styles", icon: Layers },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-20 w-64 border-r border-white/10 bg-black/30 px-4 py-5 backdrop-blur max-lg:w-60">
      <div className="mb-8 flex items-center gap-3 px-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-600">
          <Sparkles className="h-5 w-5" />
        </div>
        <div>
          <p className="font-semibold">Clip Agent</p>
          <p className="text-xs text-white/40">AI Video Workspace</p>
        </div>
      </div>

      <nav className="space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const active =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

          return (
            <Link
              key={item.label}
              href={item.href}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
                active
                  ? "bg-violet-600 text-white"
                  : "text-white/60 hover:bg-white/5 hover:text-white"
              }`}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="absolute bottom-5 left-4 right-4 rounded-2xl border border-white/10 bg-white/5 p-4">
        <p className="text-sm font-medium">Free Plan</p>
        <p className="mt-1 text-xs text-white/50">120 credits remaining</p>
        <button className="mt-3 w-full rounded-xl bg-white px-3 py-2 text-xs font-semibold text-black">
          Upgrade
        </button>
      </div>
    </aside>
  );
}
