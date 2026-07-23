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
  ReviewBadge,
  ReviewButton,
  ReviewDivider,
  ReviewEditorSurface,
  ReviewEmptyState,
  ReviewIconButton,
  ReviewKeyboardHint,
  ReviewPanel,
  ReviewPanelBody,
  ReviewPanelHeader,
  ReviewPanelTitle,
  ReviewSkeleton,
  ReviewToolbarGroup,
  reviewClassNames,
} = require(path.resolve(
  __dirname,
  "../src/features/review/design-system/index.ts",
));

function main() {
  const html =
    renderToStaticMarkup(
      React.createElement(
        ReviewEditorSurface,
        {
          variant: "base",
          className:
            "test-surface",
        },

        React.createElement(
          ReviewPanel,
          {
            variant: "active",
          },

          React.createElement(
            ReviewPanelHeader,
            null,

            React.createElement(
              ReviewPanelTitle,
              null,
              "Timeline",
            ),

            React.createElement(
              ReviewBadge,
              {
                tone: "success",
                dot: true,
              },
              "Đã lưu",
            ),
          ),

          React.createElement(
            ReviewPanelBody,
            null,

            React.createElement(
              ReviewToolbarGroup,
              null,

              React.createElement(
                ReviewButton,
                {
                  variant:
                    "primary",
                  size: "sm",
                },
                "AI Edit",
              ),

              React.createElement(
                ReviewIconButton,
                {
                  "aria-label":
                    "Undo",
                  variant:
                    "ghost",
                },
                "↶",
              ),
            ),

            React.createElement(
              ReviewDivider,
            ),

            React.createElement(
              ReviewKeyboardHint,
              null,
              "⌘K",
            ),

            React.createElement(
              ReviewSkeleton,
              {
                className: "h-8",
              },
            ),

            React.createElement(
              ReviewEmptyState,
              {
                title:
                  "Chưa có clip",

                description:
                  "Thêm clip để bắt đầu dựng.",
              },
            ),
          ),
        ),
      ),
    );

  const classNamesValid =
    reviewClassNames(
      "a",
      false,
      null,
      undefined,
      "b",
    ) === "a b";

  const checks = {
    theme_scoped:
      html.includes(
        "review-editor-theme",
      ),

    surface_variant:
      html.includes(
        'data-review-surface="base"',
      ),

    panel_variant:
      html.includes(
        'data-review-panel="active"',
      ),

    button_variant:
      html.includes(
        'data-review-button="primary"',
      ),

    icon_button_accessible:
      html.includes(
        'aria-label="Undo"',
      ),

    badge_tone:
      html.includes(
        'data-review-badge="success"',
      ),

    toolbar_semantic:
      html.includes(
        'role="group"',
      ),

    divider_semantic:
      html.includes(
        'role="separator"',
      ),

    empty_state_rendered:
      html.includes(
        "Chưa có clip",
      ),

    skeleton_rendered:
      html.includes(
        "review-skeleton",
      ),

    class_names_valid:
      classNamesValid,
  };

  console.log(
    "=== New Review Workspace Design System ===",
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
    "\nDONE: Review Workspace design system test completed.",
  );
}

main();