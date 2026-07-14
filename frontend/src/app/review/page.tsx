import { ReviewWorkspace } from "@/features/review";

const DEFAULT_PRODUCTION_ID = "221e4b01-5fb9-4b4a-a549-4fb32c455059";

export interface ReviewPageProps {
  searchParams: Promise<{
    production_id?: string | string[];
  }>;
}

export default async function ReviewPage({ searchParams }: ReviewPageProps) {
  const parameters = await searchParams;
  const requestedProductionId = parameters.production_id;
  const productionId =
    typeof requestedProductionId === "string" && requestedProductionId.trim()
      ? requestedProductionId.trim()
      : DEFAULT_PRODUCTION_ID;

  return <ReviewWorkspace productionId={productionId} />;
}
