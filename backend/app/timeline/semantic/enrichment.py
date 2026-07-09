from __future__ import annotations

from app.timeline.semantic.models import TimelineSemanticAnalysis, TimelineSemanticSegment


class TimelineSemanticEnrichmentEngine:
    def enrich(
        self,
        analysis: TimelineSemanticAnalysis,
        planner_request: dict | None = None,
        content_graph: dict | None = None,
    ) -> TimelineSemanticAnalysis:
        segment_sources = self._build_segment_sources(
            planner_request=planner_request,
            content_graph=content_graph,
        )

        enriched_segments = [
            self._enrich_segment(segment, segment_sources)
            for segment in analysis.segments
        ]

        return TimelineSemanticAnalysis(
            production_id=analysis.production_id,
            segments=enriched_segments,
            assets=analysis.assets,
            metadata={
                **analysis.metadata,
                "enrichment_engine": "TimelineSemanticEnrichmentEngine",
                "enriched_segment_count": len(enriched_segments),
                "segment_source_count": len(segment_sources),
            },
        )

    def _build_segment_sources(
        self,
        planner_request: dict | None,
        content_graph: dict | None,
    ) -> dict[str, dict]:
        sources: dict[str, dict] = {}

        if planner_request:
            for segment in planner_request.get("segments", []):
                segment_id = str(segment.get("segment_id") or segment.get("id") or "")

                if not segment_id:
                    continue

                sources[segment_id] = {
                    **segment,
                    "source": "planner_request",
                }

        if content_graph:
            for segment in content_graph.get("segments", []):
                segment_id = str(segment.get("segment_id") or segment.get("id") or "")

                if not segment_id:
                    continue

                sources[segment_id] = {
                    **sources.get(segment_id, {}),
                    **segment,
                    "source": "content_graph",
                }

        return sources

    def _enrich_segment(
        self,
        segment: TimelineSemanticSegment,
        sources: dict[str, dict],
    ) -> TimelineSemanticSegment:
        source = sources.get(segment.segment_id)

        if not source:
            return segment

        return TimelineSemanticSegment(
            segment_id=segment.segment_id,
            start_time=segment.start_time,
            end_time=segment.end_time,
            text=source.get("text", segment.text),
            segment_type=source.get("segment_type", source.get("type", segment.segment_type)),
            emotion=source.get("emotion", segment.emotion),
            importance_score=float(
                source.get("importance_score", segment.importance_score)
            ),
            viral_potential_score=float(
                source.get("viral_potential_score", segment.viral_potential_score)
            ),
            pacing=segment.pacing,
            visual_density=segment.visual_density,
            metadata={
                **segment.metadata,
                "semantic_enriched": True,
                "semantic_enrichment_source": source.get("source"),
            },
        )