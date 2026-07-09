from __future__ import annotations

from app.asset.workflow.models import MediaWorkflowRequest, MediaWorkflowResult


class MediaWorkflowRuntime:
    def build_provider_keys(
        self,
        asset_type: str,
    ) -> list[str]:
        normalized = asset_type.lower()

        if normalized in {"broll", "video"}:
            return ["pexels", "pixabay"]

        if normalized in {"sound_effect", "sfx"}:
            return ["freesound"]

        if normalized == "music":
            return ["internal_music"]

        if normalized == "image":
            return ["pexels", "pixabay"]

        return ["pexels", "pixabay"]

    def build_workflow(
        self,
        request: MediaWorkflowRequest,
    ) -> MediaWorkflowResult:
        normalized = request.asset_type.lower()
        provider_keys = self.build_provider_keys(normalized)

        if normalized in {"broll", "video"}:
            workflow_key = "video_workflow"
        elif normalized in {"sound_effect", "sfx"}:
            workflow_key = "sound_effect_workflow"
        elif normalized == "music":
            workflow_key = "music_workflow"
        elif normalized == "image":
            workflow_key = "image_workflow"
        else:
            workflow_key = "generic_media_workflow"

        return MediaWorkflowResult(
            workflow_key=workflow_key,
            query=request.query,
            asset_type=request.asset_type,
            provider_keys=provider_keys,
            metadata={
                "track_type": request.track_type,
                "preferred_duration": request.preferred_duration,
                "preferred_orientation": request.preferred_orientation,
                "commercial_use": request.commercial_use,
                "per_page": request.per_page,
                "source": "media_workflow_runtime",
            },
        )