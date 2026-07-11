from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from fastapi.testclient import TestClient

from app.main import app


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


def main() -> None:
    client = TestClient(app)

    workspace_response = client.get(
        (
            f"/api/v1/productions/"
            f"{PRODUCTION_ID}/workspace"
        ),
        params={
            "force_refresh": "true",
            "include_timeline_tracks": "true",
        },
    )

    print(
        "workspace_status_code:",
        workspace_response.status_code,
    )

    if workspace_response.status_code != 200:
        print(
            "workspace_error:",
            workspace_response.text,
        )

    assert (
        workspace_response.status_code
        == 200
    )

    workspace = (
        workspace_response.json()
    )

    summary_response = client.get(
        (
            f"/api/v1/productions/"
            f"{PRODUCTION_ID}/workspace/summary"
        ),
        params={
            "force_refresh": "true",
        },
    )

    print(
        "summary_status_code:",
        summary_response.status_code,
    )

    if summary_response.status_code != 200:
        print(
            "summary_error:",
            summary_response.text,
        )

    assert (
        summary_response.status_code
        == 200
    )

    summary = summary_response.json()

    missing_response = client.get(
        (
            "/api/v1/productions/"
            "11111111-1111-1111-1111-111111111111/"
            "workspace"
        )
    )

    print(
        "missing_status_code:",
        missing_response.status_code,
    )

    assert (
        missing_response.status_code
        == 404
    )

    output = {
        "workspace": workspace,
        "summary": summary,
        "missing": missing_response.json(),
    }

    output_path = Path(
        "storage/demo_outputs/"
        "product_workspace_api.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "=== Product Workspace API ==="
    )
    print(
        "production_id:",
        workspace["production"][
            "production_id"
        ],
    )
    print(
        "status:",
        workspace["production"][
            "status"
        ],
    )
    print(
        "stage:",
        workspace["production"][
            "stage"
        ],
    )
    print(
        "timeline_available:",
        workspace["timeline"][
            "available"
        ],
    )
    print(
        "track_count:",
        workspace["timeline"][
            "track_count"
        ],
    )
    print(
        "clip_count:",
        workspace["timeline"][
            "clip_count"
        ],
    )
    print(
        "preview_available:",
        workspace["preview"][
            "available"
        ],
    )
    print(
        "quality_available:",
        workspace["quality"][
            "available"
        ],
    )
    print(
        "artifact_count:",
        len(workspace["artifacts"]),
    )
    print(
        "summary_tracks_included:",
        summary["timeline"][
            "metadata"
        ].get(
            "tracks_included"
        ),
    )
    print("output:", output_path)

    assert (
        workspace["production"][
            "production_id"
        ]
        == PRODUCTION_ID
    )

    assert (
        workspace["timeline"][
            "available"
        ]
        is True
    )

    assert (
        workspace["timeline"][
            "track_count"
        ]
        > 0
    )

    assert (
        workspace["timeline"][
            "clip_count"
        ]
        > 0
    )

    assert (
        len(workspace["artifacts"])
        > 0
    )

    assert (
        workspace["preview"][
            "available"
        ]
        is True
    )

    assert (
        summary["timeline"][
            "tracks"
        ]
        == []
    )

    assert (
        missing_response.json()[
            "detail"
        ]["code"]
        == "production_not_found"
    )

    print(
        "\nDONE: Product workspace API "
        "test completed."
    )


if __name__ == "__main__":
    main()