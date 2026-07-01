import {
  BarChart3,
  CreditCard,
  Film,
  FolderKanban,
  Home,
  Images,
  Layers,
  Settings,
  Sparkles,
  Upload,
} from "lucide-react";

const items = [
  { label: "Dashboard", icon: Home },
  { label: "Projects", icon: FolderKanban },
  { label: "Upload", icon: Upload },
  { label: "AI Studio", icon: Sparkles },
  { label: "Templates", icon: Layers },
  { label: "Assets", icon: Images },
  { label: "Render Queue", icon: Film },
  { label: "Analytics", icon: BarChart3 },
  { label: "Billing", icon: CreditCard },
  { label: "Settings", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 w-64 border-r border-white/10 bg-black/30 px-4 py-5">
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
        {items.map((item, index) => {
          const Icon = item.icon;
          const active = index === 0;

          return (
            <button
              key={item.label}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
                active
                  ? "bg-violet-600 text-white"
                  : "text-white/60 hover:bg-white/5 hover:text-white"
              }`}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </button>
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
