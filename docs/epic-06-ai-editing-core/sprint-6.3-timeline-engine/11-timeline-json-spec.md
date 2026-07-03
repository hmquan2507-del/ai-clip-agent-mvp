# Timeline JSON Specification

Status: Draft

Version: 1.0

Owner: AI Clip Agent

---

# Purpose

Timeline JSON is the canonical editing format of AI Clip Agent.

It represents every editing decision in a deterministic, machine-readable structure.

Every component of the platform communicates through Timeline JSON.

The Renderer never receives prompts.

The Renderer only receives Timeline JSON.

---

# Philosophy

AI makes decisions.

Timeline stores decisions.

Renderer executes decisions.

No rendering logic should contain AI reasoning.

---

# High-Level Structure

Timeline

├── Metadata
├── Production
├── Tracks
├── Segments
├── Events
├── Assets
├── Styles
├── Rules
└── Render Settings

---

# Timeline Root

{
  "version": "1.0",
  "production": {},
  "metadata": {},
  "timeline": {},
  "render": {}
}

---

# Metadata

Stores information about timeline generation.

Example

{
  "generated_at": "...",
  "generator": "AI Clip Agent",
  "version": "1.0",
  "duration": 74.52,
  "fps": 30
}

---

# Production

{
    "id": "...",
    "workspace_id": "...",
    "title": "...",
    "style": "Business",
    "language": "vi"
}

---

# Timeline

Timeline

↓

Tracks

↓

Events

↓

Assets

---

# Track

Every media type has its own track.

Example

tracks:

video

broll

subtitle

music

sfx

overlay

cta

voice

---

# Event

Everything rendered is an Event.

Event

↓

Start

↓

End

↓

Asset

↓

Parameters

↓

Animation

↓

Transition

---

Example

{
  "id":"event_001",

  "track":"subtitle",

  "type":"subtitle",

  "start":12.2,

  "end":14.9,

  "asset":"subtitle_default",

  "parameters":{

      "text":"AI giúp tiết kiệm thời gian."

  }

}

---

# Asset Reference

Timeline never stores media.

Timeline only references assets.

Example

{
  "asset_id":"BR00451",

  "type":"broll"
}

---

# Parameters

Each Event contains custom parameters.

Subtitle

text

font

color

alignment

animation

Music

volume

fade_in

fade_out

loop

B-roll

crop

opacity

scale

transition

CTA

button

text

position

animation

---

# Transition

Every Event may contain transitions.

Supported

Fade

Slide

Zoom

Cut

Blur

None

---

# Animation

Supported

Bounce

Scale

Shake

Fade

Slide

Glow

Pop

---

# Segment

Timeline is divided into logical segments.

Hook

↓

Problem

↓

Explanation

↓

Example

↓

Solution

↓

CTA

↓

Outro

---

# Editing Rules

Timeline stores which rule created each event.

Example

{
   "rule":"highlight_keyword"
}

This enables debugging and AI improvement.

---

# Style

Each Timeline references one Style Profile.

Example

{
   "style":"Business"
}

Renderer loads style configuration automatically.

---

# Render Settings

Resolution

FPS

Codec

Bitrate

Audio

Platform

Example

{
   "resolution":"1080x1920",

   "fps":30,

   "codec":"H264"
}

---

# Validation Rules

Every Timeline must satisfy:

Valid timestamps

No overlapping events inside same track

Existing assets

Known styles

Known rules

Positive duration

Track consistency

---

# Example Timeline

Timeline

↓

Video Track

↓

Original Video

↓

Subtitle Track

↓

Subtitle Events

↓

B-roll Track

↓

B-roll Events

↓

Music Track

↓

Background Music

↓

CTA Track

↓

Call To Action

↓

Renderer

↓

MP4

---

# Versioning

Timeline versions are immutable.

Renderer v1 supports

Timeline v1

Future Timeline versions must remain backward compatible whenever possible.

---

# Future Expansion

Nested Timelines

Collaborative Editing

AI Feedback

Realtime Editing

Interactive Timeline

Timeline Marketplace

Plugin Events

3D Layers

Motion Graph

Smart Effects

---

# Long-term Vision

Timeline JSON becomes the universal editing language of AI Clip Agent.

Every AI model, editing engine, renderer, plugin, and third-party integration should communicate through this specification.

The Timeline is not merely a render instruction.

It is the executable representation of an AI-generated video.