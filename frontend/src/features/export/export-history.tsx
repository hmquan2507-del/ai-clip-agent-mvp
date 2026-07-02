import { Download, FileVideo } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  exportHistory,
  exportStatusLabel,
  exportStatusTone,
} from "@/lib/mock-export";

export function ExportHistory() {
  return (
    <Card>
      <CardHeader
        title="Export History"
        description="Previous export jobs for this Production."
      />

      <CardContent>
        <div className="space-y-3">
          {exportHistory.map((item) => (
            <div
              key={item.id}
              className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"
            >
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="flex gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-500/10 text-violet-300">
                    <FileVideo className="h-5 w-5" />
                  </div>

                  <div>
                    <div className="flex flex-wrap gap-2">
                      <Badge tone={exportStatusTone[item.status]}>
                        {exportStatusLabel[item.status]}
                      </Badge>

                      <Badge>{item.version}</Badge>
                    </div>

                    <p className="mt-2 text-sm text-slate-300">
                      {item.resolution} • {item.format}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {item.createdAt}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-sm text-slate-400">
                    {item.fileSize}
                  </span>

                  {item.status === "completed" && (
                    <Button size="sm">
                      <Download className="h-4 w-4" />
                      Download
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}