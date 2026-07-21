from __future__ import annotations

import ast
import json
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = (
    BACKEND_ROOT
    / "storage"
    / "demo_outputs"
    / "review_multi_select_editing_api_contracts.json"
)


def read(relative_path: str) -> str:
    return (BACKEND_ROOT / relative_path).read_text(encoding="utf-8")


def main() -> None:
    contracts = read("app/review/api/contracts.py")
    schemas = read("app/review/api/schemas.py")
    router = read("app/review/api/router.py")
    interfaces = read("app/review/application/interfaces.py")
    service = read("app/review/application/service.py")
    runtime = read("app/review/editing/runtime.py")
    history = read("app/review/editing/history/runtime.py")

    for source in (contracts, schemas, router, interfaces, service, runtime, history):
        ast.parse(source)

    operations = ("MOVE_CLIPS", "DUPLICATE_CLIPS", "DELETE_CLIPS")
    routes = (
        "/timeline/multi/move",
        "/timeline/multi/duplicate",
        "/timeline/multi/delete",
    )
    methods = ("move_clips", "duplicate_clips", "delete_clips")

    checks = {
        "contract_version_valid": 'REVIEW_MULTI_SELECT_API_CONTRACT_VERSION = "16.7.7"' in contracts,
        "operations_complete": all(operation in contracts for operation in operations),
        "schemas_complete": all(name in schemas for name in ("MoveTimelineClipsRequest", "DuplicateTimelineClipsRequest", "DeleteTimelineClipsRequest")),
        "minimum_two_unique_required": "at least two unique clips" in schemas,
        "routes_complete": all(route in router for route in routes),
        "interface_complete": all(f"def {method}(" in interfaces for method in methods),
        "service_complete": all(f"def {method}(" in service for method in methods),
        "shared_command_boundary": service.count("self._execute_timeline_command(") >= 12,
        "history_backed_once": all(f"def {method}(" in history for method in methods),
        "batch_commit_used": runtime.count("self._commit_batch(") >= 5,
        "controller_has_no_runtime_access": "history_runtime" not in router and "mutation_runtime" not in router,
    }
    assert all(checks.values()), checks

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(checks, indent=2), encoding="utf-8")

    print("=== Multi-select Editing API Contracts ===")
    for name, valid in checks.items():
        print(f"{name}: {valid}")
    print(f"output: {OUTPUT_PATH.relative_to(BACKEND_ROOT)}")
    print("\nDONE: Multi-select editing API contracts test completed.")


if __name__ == "__main__":
    main()
