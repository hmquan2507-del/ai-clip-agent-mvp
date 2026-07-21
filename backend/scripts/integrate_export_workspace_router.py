from __future__ import annotations

from pathlib import Path


def main() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    main_path = backend_root / "app" / "main.py"
    source = main_path.read_text(encoding="utf-8")

    import_line = (
        "from app.review.export_api.router import "
        "router as export_workspace_router"
    )
    include_line = "app.include_router(export_workspace_router)"

    changed = False

    if import_line not in source:
        anchor = "from app.api.v1.ai_provider_health import router as ai_provider_health_router"
        if anchor not in source:
            raise RuntimeError(
                "Unable to find the router import anchor in app/main.py."
            )
        source = source.replace(
            anchor,
            anchor + "\n" + import_line,
            1,
        )
        changed = True

    if include_line not in source:
        anchor = "app.include_router(ai_provider_health_router, prefix=\"/api/v1\")"
        if anchor not in source:
            raise RuntimeError(
                "Unable to find the router registration anchor in app/main.py."
            )
        source = source.replace(
            anchor,
            anchor + "\n" + include_line,
            1,
        )
        changed = True

    if changed:
        main_path.write_text(source, encoding="utf-8")
        print(f"Integrated Export Workspace router: {main_path}")
    else:
        print(f"Export Workspace router already integrated: {main_path}")


if __name__ == "__main__":
    main()
