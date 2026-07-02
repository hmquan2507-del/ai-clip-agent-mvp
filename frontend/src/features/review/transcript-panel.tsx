import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { transcriptSegments } from "@/lib/mock-review";

export function TranscriptPanel() {
  return (
    <Card>
      <CardHeader
        title="Transcript"
        description="Review speech recognition output and jump through key moments."
      />

      <CardContent>
        <div className="space-y-3">
          {transcriptSegments.map((segment) => (
            <button
              key={segment.id}
              type="button"
              className="w-full rounded-2xl border border-slate-800 bg-slate-950/60 p-4 text-left transition hover:border-slate-700 hover:bg-slate-900"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Badge tone="neutral">{segment.speaker}</Badge>
                  <span className="text-xs text-slate-500">
                    {segment.start} - {segment.end}
                  </span>
                </div>

                <Badge tone={segment.confidence >= 0.9 ? "success" : "warning"}>
                  {Math.round(segment.confidence * 100)}%
                </Badge>
              </div>

              <p className="mt-3 text-sm leading-6 text-slate-300">
                {segment.text}
              </p>
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
