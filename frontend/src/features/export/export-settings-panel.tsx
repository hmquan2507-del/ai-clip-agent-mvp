"use client";

import { CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { exportPresets } from "@/lib/mock-export";

type ExportSettingsPanelProps = {
  selectedPresetId: string;
  onSelectPreset: (presetId: string) => void;
};

export function ExportSettingsPanel({
  selectedPresetId,
  onSelectPreset,
}: ExportSettingsPanelProps) {
  return (
    <Card>
      <CardHeader
        title="Export Settings"
        description="Choose the output preset for your approved Production."
      />

      <CardContent>
        <div className="grid gap-3">
          {exportPresets.map((preset) => {
            const selected = preset.id === selectedPresetId;

            return (
              <button
                key={preset.id}
                type="button"
                onClick={() => onSelectPreset(preset.id)}
                className={[
                  "rounded-2xl border p-4 text-left transition",
                  selected
                    ? "border-violet-500 bg-violet-500/10"
                    : "border-slate-800 bg-slate-950/60 hover:border-slate-700 hover:bg-slate-900",
                ].join(" ")}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="font-semibold text-white">
                        {preset.label}
                      </h4>

                      {selected && (
                        <Badge tone="violet">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          Selected
                        </Badge>
                      )}
                    </div>

                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      {preset.description}
                    </p>
                  </div>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  <Badge>{preset.resolution}</Badge>
                  <Badge>{preset.format}</Badge>
                </div>
              </button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}