import { Maximize2, Pause, Play, Volume2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export function VideoPreviewPanel() {
  return (
    <Card className="overflow-hidden">
      <CardHeader
        title="Video Preview"
        description="Preview AI-generated output before approval."
      />

      <CardContent>
        <div className="relative flex aspect-video items-center justify-center overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-950 via-slate-900 to-violet-950/40">
          <div className="absolute left-4 top-4">
            <Badge tone="success">Review Ready</Badge>
          </div>

          <div className="text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-white/10 text-white backdrop-blur">
              <Play className="h-7 w-7 fill-white" />
            </div>

            <p className="mt-4 text-sm text-slate-300">
              AI preview output
            </p>
          </div>

          <div className="absolute bottom-4 left-4 right-4">
            <div className="rounded-2xl border border-white/10 bg-black/40 p-3 backdrop-blur">
              <div className="mb-3 h-1.5 overflow-hidden rounded-full bg-white/10">
                <div className="h-full w-[38%] rounded-full bg-violet-500" />
              </div>

              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm">
                    <Play className="h-4 w-4" />
                  </Button>

                  <Button variant="ghost" size="sm">
                    <Pause className="h-4 w-4" />
                  </Button>

                  <Button variant="ghost" size="sm">
                    <Volume2 className="h-4 w-4" />
                  </Button>

                  <span className="text-xs text-slate-300">
                    00:58 / 02:34
                  </span>
                </div>

                <Button variant="ghost" size="sm">
                  <Maximize2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}