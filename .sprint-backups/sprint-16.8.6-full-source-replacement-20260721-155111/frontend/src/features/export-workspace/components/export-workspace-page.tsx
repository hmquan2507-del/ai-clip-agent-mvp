"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ExportRuntimePanel } from "./export-runtime-panel";
import {
  readReviewToExportContract,
} from "../navigation/review-to-export";
import type { ExportRenderContract } from "../runtime/types";

export type ExportWorkspacePageProps = {
  productionId?: string;
};

export function ExportWorkspacePage({
  productionId,
}: ExportWorkspacePageProps) {
  const [contract, setContract] =
    useState<ExportRenderContract | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setContract(
      readReviewToExportContract(productionId),
    );
    setHydrated(true);
  }, [productionId]);

  const reviewHref = productionId
    ? `/review?production_id=${encodeURIComponent(productionId)}`
    : "/review";

  return (
    <main className="min-h-screen bg-[#08090d] px-4 py-6 text-white md:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm text-white/50">
              Review → Export
            </p>
            <h1 className="mt-1 text-3xl font-semibold">
              Export Workspace
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-white/55">
              Submit the immutable Review Workspace contract and track
              render progress from the queue runtime.
            </p>
          </div>

          <Link
            href={reviewHref}
            className="rounded-xl border border-white/15 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/5"
          >
            Back to review
          </Link>
        </header>

        <section className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-lg font-semibold">
              Render handoff
            </h2>

            {!hydrated ? (
              <p className="mt-4 text-sm text-white/55">
                Loading Review Workspace contract…
              </p>
            ) : contract ? (
              <dl className="mt-5 grid gap-3 text-sm">
                <div className="flex justify-between gap-6">
                  <dt className="text-white/50">Production</dt>
                  <dd className="truncate font-mono text-white/80">
                    {contract.production_id}
                  </dd>
                </div>
                <div className="flex justify-between gap-6">
                  <dt className="text-white/50">Snapshot</dt>
                  <dd className="truncate font-mono text-white/80">
                    {contract.snapshot_id}
                  </dd>
                </div>
                <div className="flex justify-between gap-6">
                  <dt className="text-white/50">Timeline revision</dt>
                  <dd className="text-white/80">
                    {contract.timeline_revision}
                  </dd>
                </div>
                <div className="flex justify-between gap-6">
                  <dt className="text-white/50">Checksum</dt>
                  <dd className="max-w-[70%] truncate font-mono text-white/80">
                    {contract.checksum}
                  </dd>
                </div>
              </dl>
            ) : (
              <div className="mt-5 rounded-xl border border-amber-400/20 bg-amber-400/5 p-4">
                <p className="font-medium text-amber-100">
                  No immutable render contract found
                </p>
                <p className="mt-2 text-sm text-amber-100/65">
                  Return to Review Workspace and use the Export action
                  after a valid render handoff contract is available.
                </p>
              </div>
            )}
          </div>

          <ExportRuntimePanel contract={contract} />
        </section>
      </div>
    </main>
  );
}
