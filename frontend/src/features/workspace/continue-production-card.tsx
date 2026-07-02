import { ArrowRight, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ButtonLink } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  type Production,
  statusLabel,
  statusTone,
} from "@/lib/mock-productions";

type ContinueProductionCardProps = {
  production: Production;
};

export function ContinueProductionCard({
  production,
}: ContinueProductionCardProps) {
  return (
    <Card className="bg-gradient-to-br from-slate-900 to-violet-950/40">
      <CardHeader
        title="Continue Production"
        description="Production gần nhất cần bạn tiếp tục xử lý."
      />

      <CardContent>
        <div className="flex gap-4">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300">
            <Sparkles className="h-6 w-6" />
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={statusTone[production.status]}>
                {statusLabel[production.status]}
              </Badge>
              <Badge>{production.style}</Badge>
            </div>

            <h3 className="mt-4 text-xl font-semibold text-white">
              {production.title}
            </h3>

            <p className="mt-2 text-sm leading-6 text-slate-400">
              {production.description}
            </p>

            <div className="mt-5">
              <Progress
                value={production.progress}
                label="Production progress"
                helperText={`${production.progress}%`}
              />
            </div>

            <div className="mt-5 flex flex-wrap items-center gap-3">
              <ButtonLink href="/review" size="sm">
                Continue Review
                <ArrowRight className="h-4 w-4" />
              </ButtonLink>

              <ButtonLink href="/productions" variant="ghost" size="sm">
                View Details
              </ButtonLink>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}