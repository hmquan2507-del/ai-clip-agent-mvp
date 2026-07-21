import type { ExportRenderContract } from "../runtime/types";

export const REVIEW_EXPORT_STORAGE_KEY =
  "ai-clip-agent:review-to-export-contract:v1";

export type ReviewToExportEnvelope = {
  version: "1";
  productionId: string;
  storedAt: string;
  contract: ExportRenderContract;
};

export function isExportRenderContract(
  value: unknown,
): value is ExportRenderContract {
  if (!value || typeof value !== "object") {
    return false;
  }

  const candidate = value as Record<string, unknown>;

  return (
    typeof candidate.snapshot_id === "string" &&
    candidate.snapshot_id.length > 0 &&
    typeof candidate.production_id === "string" &&
    candidate.production_id.length > 0 &&
    typeof candidate.timeline_revision === "number" &&
    Number.isInteger(candidate.timeline_revision) &&
    candidate.timeline_revision >= 0 &&
    Boolean(candidate.timeline) &&
    typeof candidate.timeline === "object" &&
    typeof candidate.created_at === "string" &&
    typeof candidate.checksum === "string" &&
    candidate.checksum.length > 0
  );
}

export function extractExportRenderContract(
  snapshot: unknown,
): ExportRenderContract | null {
  if (isExportRenderContract(snapshot)) {
    return snapshot;
  }

  if (!snapshot || typeof snapshot !== "object") {
    return null;
  }

  const source = snapshot as Record<string, unknown>;
  const candidates = [
    source.render_contract,
    source.review_render_contract,
    source.export_contract,
    source.handoff_contract,
  ];

  for (const candidate of candidates) {
    if (isExportRenderContract(candidate)) {
      return candidate;
    }
  }

  return null;
}

export function buildExportWorkspaceHref(
  productionId: string,
): string {
  const query = new URLSearchParams({
    production_id: productionId,
    source: "review",
  });

  return `/export?${query.toString()}`;
}

export function storeReviewToExportContract(
  contract: ExportRenderContract,
  storage: Pick<Storage, "setItem"> = window.sessionStorage,
): ReviewToExportEnvelope {
  const envelope: ReviewToExportEnvelope = {
    version: "1",
    productionId: contract.production_id,
    storedAt: new Date().toISOString(),
    contract,
  };

  storage.setItem(
    REVIEW_EXPORT_STORAGE_KEY,
    JSON.stringify(envelope),
  );

  return envelope;
}

export function readReviewToExportContract(
  expectedProductionId?: string,
  storage: Pick<Storage, "getItem"> = window.sessionStorage,
): ExportRenderContract | null {
  const raw = storage.getItem(REVIEW_EXPORT_STORAGE_KEY);

  if (!raw) {
    return null;
  }

  try {
    const envelope = JSON.parse(raw) as Partial<ReviewToExportEnvelope>;

    if (
      envelope.version !== "1" ||
      !isExportRenderContract(envelope.contract)
    ) {
      return null;
    }

    if (
      expectedProductionId &&
      envelope.contract.production_id !== expectedProductionId
    ) {
      return null;
    }

    return envelope.contract;
  } catch {
    return null;
  }
}
