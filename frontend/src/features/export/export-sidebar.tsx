import { CheckCircle2, FileVideo } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { exportProduction } from "@/lib/mock-export";
import { DownloadSharePanel } from "./download-share-panel";

export function ExportSidebar() {
  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader
          title="Export Summary"
          description="Approved Production ready for export."
        />

        <CardContent>
          <div className="flex gap-3">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-300">
              <CheckCircle2 className="h-6 w-6" />
            </div>

            <div className="min-w-0">
              <div className="flex flex-wrap gap-2">
                <Badge tone="success">Approved</Badge>
                <Badge>{exportProduction.style}</Badge>
              </div>

              <h3 className="mt-4 text-lg font-semibold text-white">
                {exportProduction.title}
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                Duration: {exportProduction.duration}
              </p>
            </div>
          </div>

          <div className="mt-6">
            <Progress
              value={100}
              label="Export readiness"
              helperText="100%"
            />
          </div>

          <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
            <div className="flex items-center gap-2 text-slate-300">
              <FileVideo className="h-4 w-4" />
              <span className="text-sm font-medium">Output Format</span>
            </div>

            <p className="mt-2 text-sm text-slate-500">
              MP4 export with subtitles, audio mix, and final render output.
            </p>
          </div>
        </CardContent>
      </Card>

      <DownloadSharePanel />
    </div>
  );
}