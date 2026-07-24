import { notFound } from "next/navigation";
import { DesktopEditorRuntimeAdapter } from "@/features/desktop-editor";

export interface EditorPageProps {
  params: Promise<{ productionId: string }>;
}

export default async function EditorPage({ params }: EditorPageProps) {
  const { productionId } = await params;
  const normalizedProductionId = decodeURIComponent(productionId).trim();

  if (!normalizedProductionId) {
    notFound();
  }

  return <DesktopEditorRuntimeAdapter productionId={normalizedProductionId} />;
}
