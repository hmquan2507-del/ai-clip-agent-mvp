const fs = require("node:fs");
const path = require("node:path");

const frontendRoot = path.resolve(__dirname, "..");

function read(relativePath) {
  const fullPath = path.join(frontendRoot, relativePath);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`Missing integration target: ${relativePath}`);
  }
  return {
    fullPath,
    source: fs.readFileSync(fullPath, "utf8"),
  };
}

function writeIfChanged(target, next) {
  if (next === target.source) {
    console.log(`Already integrated: ${path.relative(frontendRoot, target.fullPath)}`);
    return;
  }

  fs.writeFileSync(target.fullPath, next, "utf8");
  console.log(`Integrated: ${path.relative(frontendRoot, target.fullPath)}`);
}

function replaceRegexOnce(source, pattern, replacement, label) {
  if (!pattern.test(source)) {
    throw new Error(`Missing integration anchor (${label}).`);
  }

  return source.replace(pattern, replacement);
}

function integrateTopbar() {
  const target = read("src/features/review/shell/editor-topbar.tsx");
  let next = target.source;

  if (!next.includes("onExport?: () => void;")) {
    next = replaceRegexOnce(
      next,
      /(\s+onRedo\?:\s*\(\)\s*=>\s*void;\s*)(\})/,
      `$1  onExport?: () => void;\n  exportDisabled?: boolean;\n$2`,
      "topbar props",
    );
  }

  if (!/exportDisabled\s*=\s*false/.test(next)) {
    next = replaceRegexOnce(
      next,
      /(\s+onRedo,\s*)(\}\s*:\s*ReviewEditorTopbarProps\s*\))/,
      `$1  onExport,\n  exportDisabled = false,\n$2`,
      "topbar parameters",
    );
  }

  if (!/<button[\s\S]*?onClick=\{onExport\}/.test(next)) {
    next = replaceRegexOnce(
      next,
      /\s*<Link\s+href="\/export"[\s\S]*?<\/Link>/,
      `
        <button
          type="button"
          onClick={onExport}
          disabled={!onExport || exportDisabled}
          className="inline-flex h-8 items-center justify-center gap-1.5 rounded-lg bg-[var(--review-accent)] px-3 text-xs font-semibold text-white shadow-[var(--review-shadow-accent)] transition hover:bg-[var(--review-accent-hover)] disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Download className="size-3.5" />

          <span className="hidden sm:inline">
            Xuất video
          </span>
        </button>`,
      "topbar export control",
    );
  }

  if (!next.includes("<Link")) {
    next = next.replace(/import Link from "next\/link";\s*/g, "");
  }

  writeIfChanged(target, next);
}

function integrateShell() {
  const target = read("src/features/review/shell/review-editor-shell.tsx");
  let next = target.source;

  if (!next.includes("onExport?: () => void;")) {
    next = replaceRegexOnce(
      next,
      /(\s+onRedo\?:\s*\(\)\s*=>\s*void;\s*)/,
      `$1  onExport?: () => void;\n  exportDisabled?: boolean;\n`,
      "shell props",
    );
  }

  if (!/exportDisabled\s*=\s*false/.test(next)) {
    next = replaceRegexOnce(
      next,
      /(\s+onRedo,\s*)(onSelectClip,)/,
      `$1  onExport,\n  exportDisabled = false,\n  $2`,
      "shell parameters",
    );
  }

  if (!/onExport=\{onExport\}/.test(next)) {
    next = replaceRegexOnce(
      next,
      /(onRedo=\{onRedo\}\s*)/,
      `$1        onExport={onExport}\n        exportDisabled={exportDisabled}\n`,
      "shell topbar forwarding",
    );
  }

  writeIfChanged(target, next);
}

function integrateRuntimeWorkspace() {
  const target = read("src/features/review/integration/runtime-workspace.tsx");
  let next = target.source;

  if (!next.includes('from "next/navigation"')) {
    next = replaceRegexOnce(
      next,
      /^"use client";\s*/,
      `"use client";\n\nimport { useRouter } from "next/navigation";\n\n`,
      "runtime router import",
    );
  }

  if (!next.includes("storeReviewToExportContract")) {
    const reactImport = /import\s*\{\s*useCallback,\s*\}\s*from\s*"react";/;
    next = replaceRegexOnce(
      next,
      reactImport,
      `import {\n  useCallback,\n} from "react";\n\nimport {\n  buildExportWorkspaceHref,\n  extractExportRenderContract,\n  storeReviewToExportContract,\n} from "@/features/export-workspace";`,
      "runtime export imports",
    );
  }

  if (!next.includes("const renderContract =")) {
    next = replaceRegexOnce(
      next,
      /(\s+const view\s*=\s*buildReviewEditorViewModel\(\s*state,\s*\);)/,
      `$1
  const router = useRouter();
  const renderContract =
    extractExportRenderContract(
      state.snapshot,
    );
  const openExportWorkspace =
    useCallback(() => {
      if (!renderContract) {
        return;
      }

      storeReviewToExportContract(
        renderContract,
      );
      router.push(
        buildExportWorkspaceHref(
          renderContract.production_id,
        ),
      );
    }, [renderContract, router]);`,
      "runtime export callback",
    );
  }

  if (!/onExport=\{openExportWorkspace\}/.test(next)) {
    next = replaceRegexOnce(
      next,
      /(onRefresh=\{onRefresh\}\s*)/,
      `$1      onExport={openExportWorkspace}\n      exportDisabled={!renderContract}\n`,
      "runtime shell export forwarding",
    );
  }

  writeIfChanged(target, next);
}

integrateTopbar();
integrateShell();
integrateRuntimeWorkspace();
