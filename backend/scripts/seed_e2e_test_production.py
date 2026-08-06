from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # noqa: F401  (registers every table on Base.metadata)
from app.db.base import Base
from app.db.models.production import Production
from app.db.models.user import User
from app.db.models.workspace import Workspace


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", required=True)
    args = parser.parse_args()

    engine = create_engine(f"sqlite:///{args.db_path}")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()

    user = User(email="e2e-node-test@example.com")
    db.add(user)
    db.flush()

    workspace = Workspace(name="E2E Node Test Workspace", owner_id=user.id)
    db.add(workspace)
    db.flush()

    production = Production(
        workspace_id=workspace.id,
        title="E2E Node Test Production",
    )
    db.add(production)
    db.commit()

    # Only stdout output: the caller parses this line.
    print(str(production.id))

    db.close()


if __name__ == "__main__":
    main()
