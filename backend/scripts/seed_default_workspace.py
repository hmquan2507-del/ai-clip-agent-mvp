from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.db.models.user import User
from app.db.models.workspace import Workspace
from app.db.session import SessionLocal

DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"


def main() -> None:
    """Idempotently ensure the single default workspace this MVP's
    frontend/backend hardcode (`list_productions`'s default `workspace_id`,
    `apiClient.createProduction`'s default `workspace_id`) actually exists.

    Nothing ever created this row before, so the real "Create Production"
    flow in the UI has always 404'd / failed silently.
    """
    db = SessionLocal()

    existing = (
        db.query(Workspace)
        .filter(Workspace.id == DEFAULT_WORKSPACE_ID)
        .first()
    )

    if existing is not None:
        print(f"Default workspace already exists: {existing.id}")
        db.close()
        return

    owner = User(email="operator@ai-clip-agent.local", name="Operator")
    db.add(owner)
    db.flush()

    workspace = Workspace(
        id=DEFAULT_WORKSPACE_ID,
        name="Default Workspace",
        owner_id=owner.id,
    )
    db.add(workspace)
    db.commit()

    print(f"Created default workspace: {workspace.id}")
    db.close()


if __name__ == "__main__":
    main()
