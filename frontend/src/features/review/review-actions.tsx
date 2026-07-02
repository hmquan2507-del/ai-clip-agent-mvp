import { ArrowLeft, CheckCircle2, RotateCcw } from "lucide-react";
import { Button, ButtonLink } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export function ReviewActions() {
  return (
    <Card>
      <CardHeader
        title="Review Actions"
        description="Approve output or request AI regeneration."
      />

      <CardContent>
        <div className="grid gap-3">
          <Button>
            <CheckCircle2 className="h-4 w-4" />
            Approve for Export
          </Button>

          <Button variant="secondary">
            <RotateCcw className="h-4 w-4" />
            Regenerate Output
          </Button>

          <ButtonLink href="/ai-queue" variant="ghost">
            <ArrowLeft className="h-4 w-4" />
            Back to AI Queue
          </ButtonLink>
        </div>

        <p className="mt-4 text-sm leading-6 text-slate-500">
          Approval locks the current AI output for export. Regeneration sends the
          Production back into the AI processing flow.
        </p>
      </CardContent>
    </Card>
  );
}
