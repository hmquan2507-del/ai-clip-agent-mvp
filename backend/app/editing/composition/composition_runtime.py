from __future__ import annotations

from app.editing.composition.artifact_loader import TrackArtifactLoader
from app.editing.composition.layer_builder import CompositionLayerBuilder
from app.editing.composition.models import Composition
from app.editing.composition.render_order import RenderOrderBuilder


class CompositionRuntime:
    def __init__(self):
        self.artifact_loader = TrackArtifactLoader()
        self.layer_builder = CompositionLayerBuilder()
        self.render_order_builder = RenderOrderBuilder()

    def compose(
        self,
        production_id: str,
        metadata: dict,
    ) -> Composition:
        artifacts = self.artifact_loader.load_many(metadata)
        layers = self.layer_builder.build_layers(artifacts)
        render_order = self.render_order_builder.build(layers)

        return Composition(
            production_id=production_id,
            layers=layers,
            render_order=render_order,
            metadata={
                "runtime": "composition_runtime",
                "artifact_count": len(artifacts),
                "layer_count": len(layers),
                "render_order_count": len(render_order),
                "available_tracks": [
                    artifact.track_key for artifact in artifacts
                ],
            },
        )