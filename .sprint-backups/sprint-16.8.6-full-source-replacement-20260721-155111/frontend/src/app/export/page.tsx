import { ExportWorkspacePage } from "@/features/export-workspace/components/export-workspace-page";

export interface ExportPageProps {
  searchParams: Promise<{
    production_id?: string | string[];
  }>;
}

export default async function ExportPage({
  searchParams,
}: ExportPageProps) {
  const parameters = await searchParams;
  const requestedProductionId = parameters.production_id;
  const productionId =
    typeof requestedProductionId === "string" &&
    requestedProductionId.trim()
      ? requestedProductionId.trim()
      : undefined;

  return (
    <ExportWorkspacePage
      productionId={productionId}
    />
  );
}
