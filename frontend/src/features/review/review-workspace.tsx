import { ReviewRuntimeWorkspace } from "./integration";

export interface ReviewWorkspaceProps {
  productionId: string;
}

export function ReviewWorkspace({ productionId }: ReviewWorkspaceProps) {
  return <ReviewRuntimeWorkspace productionId={productionId} />;
}
