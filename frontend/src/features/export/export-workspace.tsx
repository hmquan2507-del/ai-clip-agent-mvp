"use client";

import { useState } from "react";
import { ExportHistory } from "./export-history";
import { ExportSettingsPanel } from "./export-settings-panel";
import { ExportSidebar } from "./export-sidebar";
import { RenderProgressPanel } from "./render-progress-panel";

export function ExportWorkspace() {
  const [selectedPresetId, setSelectedPresetId] = useState("tiktok");

  return (
    <section className="grid gap-6 xl:grid-cols-[1.35fr_0.75fr]">
      <div className="grid gap-6">
        <ExportSettingsPanel
          selectedPresetId={selectedPresetId}
          onSelectPreset={setSelectedPresetId}
        />

        <RenderProgressPanel progress={100} status="completed" />

        <ExportHistory />
      </div>

      <ExportSidebar />
    </section>
  );
}