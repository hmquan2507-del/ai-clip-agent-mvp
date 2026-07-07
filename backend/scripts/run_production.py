from __future__ import annotations

import json
import sys
from pathlib import Path
from uuid import UUID

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.production.orchestrator import ProductionOrchestrator


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_production.py <production_id>")
        raise SystemExit(1)

    production_id = UUID(sys.argv[1])

    db = SessionLocal()

    try:
        orchestrator = ProductionOrchestrator(db)
        result = orchestrator.run(production_id=production_id)

        print(json.dumps(result, ensure_ascii=False, indent=2))

    finally:
        db.close()


if __name__ == "__main__":
    main()