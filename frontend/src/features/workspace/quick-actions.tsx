import { Bot, Eye, UploadCloud, Video } from "lucide-react";
import { ButtonLink } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

const quickActions = [
  {
    title: "Upload video",
    description: "Tạo Production mới từ video thô.",
    href: "/upload",
    icon: UploadCloud,
  },
  {
    title: "AI Queue",
    description: "Theo dõi AI đang xử lý production.",
    href: "/ai-queue",
    icon: Bot,
  },
  {
    title: "Review output",
    description: "Kiểm tra, approve hoặc regenerate.",
    href: "/review",
    icon: Eye,
  },
  {
    title: "Export video",
    description: "Xuất video đã được approve.",
    href: "/export",
    icon: Video,
  },
];

export function QuickActions() {
  return (
    <Card>
      <CardHeader
        title="Quick Actions"
        description="Các hành động chính trong Production workflow."
      />

      <CardContent>
        <div className="grid gap-3 sm:grid-cols-2">
          {quickActions.map((action) => {
            const Icon = action.icon;

            return (
              <ButtonLink
                key={action.href}
                href={action.href}
                variant="ghost"
                className="h-auto justify-start rounded-2xl border border-slate-800 bg-slate-950/60 p-4 text-left hover:border-slate-700 hover:bg-slate-900"
              >
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-500/10 text-violet-300">
                  <Icon className="h-5 w-5" />
                </span>

                <span>
                  <span className="block font-semibold text-white">
                    {action.title}
                  </span>
                  <span className="mt-1 block text-sm leading-6 text-slate-400">
                    {action.description}
                  </span>
                </span>
              </ButtonLink>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}