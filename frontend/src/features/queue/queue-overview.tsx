import { Bot, Clock3, PlayCircle, CheckCircle2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const stats = [
  {
    label: "Waiting",
    value: 4,
    icon: Clock3,
    color: "text-amber-300",
  },
  {
    label: "Processing",
    value: 2,
    icon: Bot,
    color: "text-violet-300",
  },
  {
    label: "Ready Review",
    value: 1,
    icon: PlayCircle,
    color: "text-sky-300",
  },
  {
    label: "Completed",
    value: 18,
    icon: CheckCircle2,
    color: "text-emerald-300",
  },
];

export function QueueOverview() {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((item) => {
        const Icon = item.icon;

        return (
          <Card key={item.label}>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">
                    {item.label}
                  </p>

                  <p className="mt-2 text-3xl font-semibold text-white">
                    {item.value}
                  </p>
                </div>

                <div
                  className={`rounded-2xl bg-slate-800 p-3 ${item.color}`}
                >
                  <Icon className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </section>
  );
}