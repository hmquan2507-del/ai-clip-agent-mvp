from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import inspect, text


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.db.session import engine
REQUIRED_TABLES = [
    "users",
    "workspaces",
    "productions",
    "assets",
    "clips",
    "exports",
    "queue_jobs",
    "render_jobs",
]

REQUIRED_ENV_VARS = [
    "DATABASE_URL",
]


OPTIONAL_ENV_VARS = [
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "R2_BUCKET_NAME",
    "R2_ENDPOINT_URL",
]


def print_header() -> None:
    print("\n==============================")
    print("AI Clip Agent Health Check")
    print("==============================\n")


def pass_check(name: str) -> None:
    print(f"[PASS] {name}")


def warn_check(name: str, message: str) -> None:
    print(f"[WARN] {name}: {message}")


def fail_check(name: str, message: str) -> None:
    print(f"[FAIL] {name}: {message}")


def check_database() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        pass_check("Database connection")
        return True
    except Exception as exc:
        fail_check("Database connection", str(exc))
        return False


def check_tables() -> bool:
    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())

        ok = True

        for table in REQUIRED_TABLES:
            if table in existing_tables:
                pass_check(f"Table `{table}`")
            else:
                fail_check(f"Table `{table}`", "missing")
                ok = False

        return ok
    except Exception as exc:
        fail_check("Table inspection", str(exc))
        return False


def check_environment() -> bool:
    ok = True

    for key in REQUIRED_ENV_VARS:
        if os.getenv(key):
            pass_check(f"Env `{key}`")
        else:
            fail_check(f"Env `{key}`", "missing")
            ok = False

    for key in OPTIONAL_ENV_VARS:
        if os.getenv(key):
            pass_check(f"Env `{key}`")
        else:
            warn_check(f"Env `{key}`", "not configured")

    return ok


def check_storage_dirs() -> bool:
    storage_paths = [
        ROOT_DIR / "storage",
        ROOT_DIR / "uploads",
    ]

    ok = True

    for path in storage_paths:
        if path.exists():
            pass_check(f"Directory `{path.name}`")
        else:
            warn_check(f"Directory `{path.name}`", "not found")
            ok = False

    return ok


def main() -> None:
    print_header()

    results = [
        check_environment(),
        check_database(),
        check_tables(),
        check_storage_dirs(),
    ]

    print("\nSystem Status:")

    if all(results):
        print("HEALTHY\n")
        raise SystemExit(0)

    print("UNHEALTHY\n")
    raise SystemExit(1)


if __name__ == "__main__":
    main()