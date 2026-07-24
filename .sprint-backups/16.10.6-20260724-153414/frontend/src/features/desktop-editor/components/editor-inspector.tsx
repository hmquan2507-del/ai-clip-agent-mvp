"use client";

import { useState } from "react";
import { Sparkles, SlidersHorizontal } from "lucide-react";

import type { ReviewAICommandBarProps } from "../../review/shell";
import type { AiCopilotSuggestion, EditorInspectorTabKey } from "../types";
import { EditorAiCopilot } from "./editor-ai-copilot";
import { PanelCollapseButton } from "./panel-collapse-button";

const PROPERTY_SECTIONS = [
  "Video",
  "Audio",
  "Text",
  "Animation",
  "Transform",
  "Effects",
  "Transitions",
];

export interface EditorInspectorProps {
  aiCommand?: ReviewAICommandBarProps;
  onAiSuggestionSelect?: (suggestion: AiCopilotSuggestion) => void;
  collapsed?: boolean;
  onToggleCollapsed?: () => void;
}

export function EditorInspector({
  aiCommand,
  onAiSuggestionSelect,
  collapsed = false,
  onToggleCollapsed,
}: EditorInspectorProps) {
  const [activeTab, setActiveTab] = useState<EditorInspectorTabKey>("ai-copilot");

  if (collapsed) {
    return (
      <aside
        aria-label="Inspector"
        className="flex h-full w-full flex-col items-center gap-2 border-l border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-surface)] py-2"
      >
        <PanelCollapseButton direction="left" label="Expand inspector" onClick={() => onToggleCollapsed?.()} />
        <span className="mt-1 rotate-180 text-[10px] font-medium tracking-[0.16em] text-[var(--desktop-editor-text-subtle)] [writing-mode:vertical-rl]">
          INSPECTOR
        </span>
      </aside>
    );
  }

  return (
    <aside
      aria-label="Inspector"
      className="flex h-full w-full min-h-0 flex-col border-l border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-surface)]"
    >
      <div className="flex h-9 shrink-0 items-center border-b border-[var(--desktop-editor-border-subtle)] px-1">
        <TabButton
          label="Properties"
          icon={SlidersHorizontal}
          active={activeTab === "properties"}
          onClick={() => setActiveTab("properties")}
        />
        <TabButton
          label="AI Copilot"
          icon={Sparkles}
          active={activeTab === "ai-copilot"}
          onClick={() => setActiveTab("ai-copilot")}
        />
        <PanelCollapseButton direction="right" label="Collapse inspector" onClick={() => onToggleCollapsed?.()} />
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {activeTab === "properties" ? (
          <PropertiesPlaceholder />
        ) : (
          <EditorAiCopilot aiCommand={aiCommand} onSuggestionSelect={onAiSuggestionSelect} />
        )}
      </div>
    </aside>
  );
}

function TabButton({
  label,
  icon: Icon,
  active,
  onClick,
}: {
  label: string;
  icon: typeof Sparkles;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={
        active
          ? "flex h-full flex-1 items-center justify-center gap-1.5 border-b-2 border-[var(--desktop-editor-primary)] text-[11px] font-semibold text-[var(--desktop-editor-text)]"
          : "flex h-full flex-1 items-center justify-center gap-1.5 text-[11px] font-medium text-[var(--desktop-editor-text-subtle)] transition hover:text-[var(--desktop-editor-text)]"
      }
    >
      <Icon className="size-3.5" />
      {label}
    </button>
  );
}

function PropertiesPlaceholder() {
  return (
    <div className="space-y-1 p-2">
      {PROPERTY_SECTIONS.map((section) => (
        <div
          key={section}
          className="rounded-[var(--desktop-editor-radius-control)] border border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-bg)] p-3"
        >
          <p className="text-[11px] font-semibold text-[var(--desktop-editor-text)]">{section}</p>
          <p className="mt-1 text-[10px] leading-4 text-[var(--desktop-editor-text-subtle)]">
            Coming soon — {section.toLowerCase()} controls will live here.
          </p>
        </div>
      ))}
    </div>
  );
}
