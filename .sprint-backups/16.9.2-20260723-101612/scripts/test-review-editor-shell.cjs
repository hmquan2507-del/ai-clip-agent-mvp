/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require(
  "node:assert/strict",
);
const fs = require("node:fs");
const path = require("node:path");
const React = require("react");

const {
  renderToStaticMarkup,
} = require("react-dom/server");

const ts = require("typescript");

function compileTypeScript(
  module,
  filename,
) {
  const source = fs.readFileSync(
    filename,
    "utf8",
  );

  const output = ts.transpileModule(
    source,
    {
      fileName: filename,
      compilerOptions: {
        target:
          ts.ScriptTarget.ES2022,

        module:
          ts.ModuleKind.CommonJS,

        moduleResolution:
          ts.ModuleResolutionKind
            .NodeJs,

        jsx:
          ts.JsxEmit.ReactJSX,

        esModuleInterop: true,
      },
    },
  );

  module._compile(
    output.outputText,
    filename,
  );
}

require.extensions[".ts"] =
  compileTypeScript;

require.extensions[".tsx"] =
  compileTypeScript;

const {
  ReviewEditorShell,
} = require(path.resolve(
  __dirname,
  "../src/features/review/shell/index.ts",
));

function main() {
  const html =
    renderToStaticMarkup(
      React.createElement(
        ReviewEditorShell,
      ),
    );

  const checks = {
    editor_theme_applied:
      html.includes(
        "review-editor-theme",
      ),

    full_height_shell:
      html.includes("h-dvh"),

    topbar_rendered:
      html.includes(
        "Video bán hàng · Bản AI dựng",
      ),

    export_action_rendered:
      html.includes("Xuất video"),

    tool_rail_rendered:
      html.includes(
        'aria-label="Công cụ dựng video"',
      ),

    preview_rendered:
      html.includes(
        "VIDEO KHÔNG RA ĐƠN",
      ),

    inspector_rendered:
      html.includes(
        "Đề xuất từ AI",
      ),

    timeline_rendered:
      html.includes(
        'aria-label="Timeline dựng video"',
      ),

    timeline_tracks_rendered:
      html.includes("Video chính") &&
      html.includes("B-roll") &&
      html.includes("Phụ đề") &&
      html.includes("Nhạc nền"),

    ai_command_rendered:
      html.includes(
        'aria-label="Ra lệnh cho AI Editor"',
      ),

    responsive_layout_present:
      html.includes(
        "max-xl:grid-cols",
      ) &&
      html.includes(
        "max-md:grid-cols-1",
      ),

    fixture_is_read_only:
      !html.includes(
        "production_not_found",
      ),
    ai_command_is_bottom_bar:
    html.includes(
    'data-review-command-bar="true"',
  ) &&
  html.indexOf(
    'aria-label="Timeline dựng video"',
  ) <
    html.indexOf(
      'data-review-command-bar="true"',
    ),
  };

  console.log(
    "=== New Review Workspace Shell ===",
  );

  for (
    const [name, value]
    of Object.entries(checks)
  ) {
    console.log(
      `${name}: ${value}`,
    );

    assert.equal(
      value,
      true,
      `${name} failed`,
    );
  }

  console.log(
    "\nDONE: New Review Workspace shell test completed.",
  );
}

main();