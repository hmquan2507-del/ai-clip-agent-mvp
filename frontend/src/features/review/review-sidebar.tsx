import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { reviewProduction } from "@/lib/mock-review";
import { ReviewActions } from "./review-actions";

export function ReviewSidebar() {
  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader
          title="Production Summary"
          description="Current review target."
        />

        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge tone="success">Review Ready</Badge>
            <Badge>{reviewProduction.style}</Badge>
          </div>

          <h3 className="mt-4 text-lg font-semibold text-white">
            {reviewProduction.title}
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            Duration: {reviewProduction.duration}
          </p>

          <div className="mt-5">
            <Progress
              value={reviewProduction.progress}
              label="Review readiness"
              helperText={`${reviewProduction.progress}%`}
            />
          </div>
        </CardContent>
      </Card>

      <ReviewActions />
    </div>
  );
}
