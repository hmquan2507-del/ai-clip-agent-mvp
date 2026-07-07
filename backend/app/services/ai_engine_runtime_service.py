from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.base.metadata_manager import MetadataManager
from app.ai.base.payload_builder import ContentGraphPayloadBuilder
from app.ai.runtime import AIContext, AIRuntime
from app.ai.runtime.runtime_registry import build_default_engine_registry
from app.artifacts.runtime_store import RuntimeArtifactStore
from app.repositories.content_graph_repository import ContentGraphRepository


class AIEngineRuntimeService:
    def __init__(self, db: Session):
        self.db = db
        self.content_graph_repository = ContentGraphRepository(db)
        self.registry = build_default_engine_registry()
        self.runtime = AIRuntime()
        self.artifact_store = RuntimeArtifactStore(db)

    def run_engine(
        self,
        production_id: UUID,
        engine_key: str,
    ) -> dict[str, Any]:
        graph = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph is None:
            return {
                "production_id": str(production_id),
                "key": engine_key,
                "data": {},
                "metadata": {
                    "status": "skipped",
                    "reason": "content_graph_not_found",
                },
            }

        metadata = MetadataManager.load(graph.metadata_json)

        context = AIContext(
            production_id=str(production_id),
            payload=ContentGraphPayloadBuilder.build(graph),
            metadata=metadata,
            runtime_data=dict(metadata),
        )

        engine = self.registry.get(engine_key)

        result = self.runtime.run_engine(
            key=engine_key,
            engine=engine,
            context=context,
        )

        result_dict = result.to_dict()
        self._persist_provider_artifacts(
            production_id=str(production_id),
            engine_key=engine_key,
            result_data=result_dict["data"],
        )
        metadata_json = MetadataManager.merge_result(
            metadata_json=graph.metadata_json,
            key=engine_key,
            result=result_dict["data"],
        )

        self.content_graph_repository.update_metadata_json(
            graph_id=str(graph.id),
            metadata_json=metadata_json,
        )

        if isinstance(result_dict["data"], dict):
            self.artifact_store.save(
                production_id=str(production_id),
                artifact_key=engine_key,
                payload=result_dict["data"],
            )

        return result_dict["data"]

    def run_pipeline(
        self,
        production_id: UUID,
        engine_keys: list[str],
    ) -> dict[str, Any]:
        graph = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph is None:
            return {
                "production_id": str(production_id),
                "results": {},
                "metadata": {
                    "status": "skipped",
                    "reason": "content_graph_not_found",
                },
            }

        metadata = MetadataManager.load(graph.metadata_json)

        context = AIContext(
            production_id=str(production_id),
            payload=ContentGraphPayloadBuilder.build(graph),
            metadata=metadata,
            runtime_data=dict(metadata),
        )

        results: dict[str, Any] = {}

        for engine_key in engine_keys:
            engine = self.registry.get(engine_key)

            result = self.runtime.run_engine(
                key=engine_key,
                engine=engine,
                context=context,
            )

            result_data = result.data

            context.set_runtime_result(
                engine_key,
                result_data,
            )

            results[engine_key] = result_data
            self._persist_provider_artifacts(
                production_id=str(production_id),
                engine_key=engine_key,
                result_data=result_data,
            )

            if isinstance(result_data, dict):
                self.artifact_store.save(
                    production_id=str(production_id),
                    artifact_key=engine_key,
                    payload=result_data,
                )

        merged_metadata = dict(metadata)

        for key, value in results.items():
            merged_metadata[key] = value

        self.content_graph_repository.update_metadata_json(
            graph_id=str(graph.id),
            metadata_json=MetadataManager.dump(merged_metadata),
        )

        return {
            "production_id": str(production_id),
            "results": results,
            "metadata": {
                "engine_keys": engine_keys,
                "total_results": len(results),
            },
        }

    def _persist_provider_artifacts(
        self,
        production_id: str,
        engine_key: str,
        result_data: Any,
    ) -> None:
        if not isinstance(result_data, dict):
            return

        metadata = result_data.get("metadata", {})
        if not isinstance(metadata, dict):
            return

        gemini_hook_detection = metadata.get("gemini_hook_detection")

        if isinstance(gemini_hook_detection, dict):
            self.artifact_store.save_gemini_hook_detection(
                production_id=production_id,
                payload=gemini_hook_detection,
            )