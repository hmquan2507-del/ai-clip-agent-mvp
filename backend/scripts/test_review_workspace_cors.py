from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)

PREFLIGHT_PATH = (
    f"/api/v1/productions/"
    f"{PRODUCTION_ID}/review/session"
)


def main() -> None:
    client = TestClient(app)

    allowed_origin = settings.cors_origins[0]
    disallowed_origin = (
        "https://untrusted.example"
    )

    allowed = client.options(
        PREFLIGHT_PATH,
        headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method":
                "POST",
            "Access-Control-Request-Headers":
                "content-type,x-request-id",
        },
    )

    disallowed = client.options(
        PREFLIGHT_PATH,
        headers={
            "Origin": disallowed_origin,
            "Access-Control-Request-Method":
                "POST",
            "Access-Control-Request-Headers":
                "content-type",
        },
    )

    simple = client.get(
        "/",
        headers={
            "Origin": allowed_origin,
            "X-Request-ID":
                "review-cors-test",
        },
    )

    allow_methods = allowed.headers.get(
        "access-control-allow-methods",
        "",
    )

    allow_headers = allowed.headers.get(
        "access-control-allow-headers",
        "",
    )

    expose_headers = simple.headers.get(
        "access-control-expose-headers",
        "",
    )

    checks = {
        "origins_configured":
            bool(settings.cors_origins),

        "allowed_preflight_works":
            allowed.status_code == 200,

        "allowed_origin_echoed": (
            allowed.headers.get(
                "access-control-allow-origin",
            )
            == allowed_origin
        ),

        "credentials_allowed": (
            allowed.headers.get(
                "access-control-allow-credentials",
            )
            == "true"
        ),

        "post_method_allowed":
            "POST" in allow_methods,

        "content_type_allowed":
            "content-type"
            in allow_headers.lower(),

        "request_id_allowed":
            "x-request-id"
            in allow_headers.lower(),

        "disallowed_origin_blocked": (
            disallowed.status_code == 400
            and
            "access-control-allow-origin"
            not in disallowed.headers
        ),

        "simple_request_works":
            simple.status_code == 200,

        "simple_origin_allowed": (
            simple.headers.get(
                "access-control-allow-origin",
            )
            == allowed_origin
        ),

        "request_id_preserved": (
            simple.headers.get(
                "x-request-id",
            )
            == "review-cors-test"
        ),

        "request_id_exposed":
            "x-request-id"
            in expose_headers.lower(),
    }

    print(
        "=== Review Workspace CORS Integration ==="
    )

    for name, value in checks.items():
        print(f"{name}: {value}")
        assert value, f"{name} failed"

    print(
        "\nDONE: Review Workspace CORS "
        "integration test completed."
    )


if __name__ == "__main__":
    main()