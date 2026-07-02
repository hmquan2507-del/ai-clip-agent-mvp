import { Lightbulb, WandSparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { reviewSuggestions } from "@/lib/mock-review";

const suggestionTone = {
  highlight: "violet",
  subtitle: "info",
  broll: "warning",
  music: "success",
  cta: "neutral",
} as const;

export function AISuggestions() {
  return (
    <Card>
      <CardHeader
        title="AI Suggestions"
        description="Understand what AI selected and why."
      />

      <CardContent>
        <div className="space-y-3">
          {reviewSuggestions.map((suggestion) => (
            <div
              key={suggestion.id}
              className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"
            >
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-500/10 text-violet-300">
                  <Lightbulb className="h-5 w-5" />
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge tone={suggestionTone[suggestion.type]}>
                      {suggestion.type}
                    </Badge>
                    <Badge tone="success">{suggestion.confidence}%</Badge>
                    <span className="text-xs text-slate-500">
                      {suggestion.timestamp}
                    </span>
                  </div>

                  <h4 className="mt-3 font-semibold text-white">
                    {suggestion.title}
                  </h4>

                  <p className="mt-1 text-sm leading-6 text-slate-400">
                    {suggestion.description}
                  </p>

                  <div className="mt-4 flex gap-2">
                    <Button size="sm" variant="ghost">
                      Accept
                    </Button>
                    <Button size="sm" variant="ghost">
                      Regenerate
                      <WandSparkles className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
