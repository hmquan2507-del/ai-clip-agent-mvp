from __future__ import annotations
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.product.adapters.models import (
    ProductPreviewSummary,
    ProductQualitySummary,
    ProductTimelineSummary,
)
from app.product.contracts.models import (
    ProductProductionSnapshot,
    ProductProgress
)
from app.product.contracts.enums import ProductProductionStatus, ProductStage
from app.review import create_review_workspace_service, ReviewWorkspace

def main():
    """
    Tests the Review Workspace domain layer.
    """
    print("🚀 Starting Review Workspace Domain Test")

    # 1. Create mock data
    production_id = "prod_12345"
    mock_production = ProductProductionSnapshot(
        production_id=production_id,
        name="Test Production",
        status=ProductProductionStatus.RENDERING_PREVIEW,
        stage=ProductStage.PREVIEW_RENDER,
        progress=ProductProgress(
            stage=ProductStage.PREVIEW_RENDER,
            progress=50.0,
            message="Rendering video"
        ),
    )
    mock_timeline = {
        "version": "v2",
        "duration": 120.5,
        "tracks": [{"id": "track1"}, {"id": "track2"}, {"id": "track3"}],
    }
    mock_video_artifact = {
        "artifact_id": "art_video_123",
        "artifact_type": "preview_video",
        "download_url": "/storage/preview/prod_12345.mp4",
        "metadata": {
            "duration": 120.5,
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
        }
    }
    mock_thumb_artifact = {
        "artifact_id": "art_thumb_123",
        "artifact_type": "preview_thumbnail",
        "download_url": "/storage/preview/prod_12345.jpg",
    }
    mock_artifacts = [mock_video_artifact, mock_thumb_artifact]
    mock_quality = ProductQualitySummary(available=True, approved=False)
    mock_ai_summary = {"suggestion_count": 5, "tags": ["funny", "cat"]}

    # 2. Get the service
    review_service = create_review_workspace_service()
    print("✅ Review service created")

    # 3. Register mock data
    # The loader is shared across all loader types in our factory
    loader = review_service.product_workspace_service.production_loader
    loader.register(
        production_id,
        production=mock_production,
        timeline=mock_timeline,
        artifacts=mock_artifacts,
        quality_report=mock_quality,
        ai_summary=mock_ai_summary,
        issues=[],
    )
    print("✅ Mock data registered in in-memory loader")

    # 4. Build the workspace
    workspace = review_service.build_workspace(production_id)
    print("✅ Workspace built")

    # 5. Perform checks
    print("\n🔎 Performing checks...")
    assert workspace.production_id == production_id, "Workspace created"
    print("✅ Workspace created: PASSED")

    assert workspace.preview.available, "Preview initialized"
    assert workspace.preview.width == 1920, "Preview width is correct"
    print("✅ Preview initialized: PASSED")

    assert workspace.timeline.track_count == 3, "Timeline initialized"
    assert workspace.timeline.version == "v2", "Timeline version is correct"
    print("✅ Timeline initialized: PASSED")
    
    assert workspace.selection is not None, "Selection initialized"
    print("✅ Selection initialized: PASSED")
    
    assert workspace.ai.metadata == mock_ai_summary, "AI initialized"
    print("✅ AI initialized: PASSED")

    assert workspace.export is not None and not workspace.export.is_exported, "Export initialized"
    print("✅ Export initialized: PASSED")

    assert workspace.review is not None and not workspace.review.is_approved, "Review initialized"
    print("✅ Review initialized: PASSED")

    print("\n🎉 All checks passed!")

    # 6. Save demo JSON
    output_dir = project_root / "storage" / "demo_outputs"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "review_workspace_domain.json"
    
    with open(output_path, "w") as f:
        f.write(workspace.to_json())

    print(f"\n💾 Demo JSON saved to: {output_path}")


if __name__ == "__main__":
    main()
