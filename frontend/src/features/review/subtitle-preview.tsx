import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { subtitlePreview } from "@/lib/mock-review";

export function SubtitlePreview() {
  return (
    <Card>
      <CardHeader
        title="Subtitle Preview"
        description="Inspect generated subtitles before approval."
      />

      <CardContent>
        <div className="space-y-3">
          {subtitlePreview.map((subtitle) => (
            <div
              key={subtitle.id}
              className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"
            >
              <Badge tone="info">{subtitle.time}</Badge>

              <p className="mt-3 text-lg font-semibold leading-7 text-white">
                {subtitle.text}
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
