# Domain Model

Status: Draft  
Owner: Ho Quan  
Version: 0.1  
Related Epic: EPIC-02 AI Production Workspace  

---

## Purpose

This document defines the core business domain of AI Clip Agent.

It is the foundation for backend architecture, frontend structure, database design, API contracts, queue design, and AI pipeline orchestration.

---

## Core Domain

AI Clip Agent is centered around one core domain:

**AI Video Production**

The most important object in the system is not a Project.

The most important object is a **Production**.

A Production represents one complete AI-driven video production workflow from source video upload to final export.

---

## Domain Overview

```text
Workspace
  ↓
Production
  ↓
Source Video
  ↓
AI Pipeline
  ↓
Generated Clips
  ↓
Review
  ↓
Export
Primary Entities
Workspace

A Workspace groups users, productions, assets, styles, and billing.

A Workspace may contain many Productions.

Production

A Production is the main aggregate root.

It represents the full lifecycle of turning one source video into one or more edited videos.

A Production owns:

Source Video
AI Jobs
Generated Clips
Review State
Export Jobs
Production Status
Source Video

The original uploaded video.

It contains:

File URL
Duration
Format
Resolution
Audio metadata
Upload status
Storage provider
AI Job

An AI Job represents one stage in the production pipeline.

Examples:

Transcript Job
Scene Detection Job
Highlight Detection Job
Clip Selection Job
Subtitle Job
B-roll Job
Music Job
Sound FX Job
Render Job
Generated Clip

A Generated Clip is a short-form video candidate created by AI.

It contains:

Start time
End time
Transcript segment
Hook
Caption
Viral score
Style
Review status
Render status
Review

Review is the human approval layer.

The user should review AI output, not edit from scratch.

Review may include:

Approve clip
Reject clip
Regenerate clip
Change style
Edit subtitle
Replace B-roll
Change music
Export

Export represents the final rendered video file.

It contains:

Output URL
Platform format
Resolution
Aspect ratio
Duration
Export status
Value Objects
Style

A Style defines how AI edits a video.

Examples:

Talking Head
Podcast
Education
Business
Finance
Storytelling
Gaming
Luxury

A Style controls:

Subtitle style
B-roll behavior
Music behavior
Sound FX behavior
Zoom behavior
Motion behavior
CTA behavior
Production Status

Possible statuses:

draft
uploading
uploaded
analyzing
generating_clips
editing
rendering
ready_for_review
exporting
completed
failed
AI Job Status

Possible statuses:

pending
running
succeeded
failed
skipped
cancelled
Clip Review Status

Possible statuses:

pending_review
approved
rejected
needs_changes
regenerating
Domain Events

Important events:

ProductionCreated
SourceVideoUploaded
TranscriptCompleted
HighlightsDetected
ClipsGenerated
ClipReadyForReview
ClipApproved
RenderStarted
RenderCompleted
ExportCompleted
ProductionFailed

Domain events will be used later for queue workers, notifications, analytics, and automation.

Bounded Contexts
Production Context

Owns the Production lifecycle.

Upload Context

Owns video upload, storage, metadata, and ingestion.

AI Context

Owns transcript, highlight detection, clip generation, style application, and AI model routing.

Review Context

Owns approval, rejection, regeneration, and manual adjustment.

Export Context

Owns rendering, platform formats, output files, and download links.

Billing Context

Owns usage limits, credits, plans, and payment.

Lifecycle
Create Production

↓

Upload Source Video

↓

Analyze Video

↓

Generate Clips

↓

Apply Style

↓

Render Drafts

↓

Review Clips

↓

Approve Clips

↓

Export Final Videos

↓

Complete Production
Key Design Decisions
Production over Project

The system should use Production as the main concept.

Project is too broad and may confuse the product direction.

Review over Edit

The user should not be forced into a timeline editor by default.

AI should produce first.

The user should review and approve.

Pipeline over Manual Workflow

The system should behave like a production pipeline, not a manual editing tool.

Style as a First-Class Concept

Style is not a visual preset only.

Style is an AI editing recipe.

Open Questions
Should one Production support multiple source videos?
Should one Production generate multiple style variants?
Should Style be user-customizable in MVP?
Should Render be part of AI Context or Export Context?
Should Review happen before or after draft rendering?
Future Improvements
Multi-video productions
Team review workflow
Batch production
Social publishing
AI quality scoring
Auto-regeneration
Enterprise approval workflow
