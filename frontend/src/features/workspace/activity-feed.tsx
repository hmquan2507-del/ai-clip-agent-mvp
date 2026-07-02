import { Clock } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { activityItems } from "@/lib/mock-productions";

export function ActivityFeed() {
  return (
    <Card>
      <CardHeader
        title="Workspace Activity"
        description="Những thay đổi mới nhất trong workspace."
      />

      <CardContent>
        <div className="space-y-5">
          {activityItems.map((item) => (
            <div key={item.id} className="flex gap-3">
              <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-800 text-slate-400">
                <Clock className="h-4 w-4" />
              </div>

              <div>
                <p className="font-medium text-white">{item.title}</p>
                <p className="mt-1 text-sm leading-6 text-slate-400">
                  {item.description}
                </p>
                <p className="mt-1 text-xs text-slate-500">{item.time}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}