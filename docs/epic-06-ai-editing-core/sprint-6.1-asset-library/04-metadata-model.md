# Asset Metadata Model

Status: Draft

Version: 1.0

---

# Purpose

Every asset stored inside AI Clip Agent must contain structured metadata.

The AI should never search raw video files directly.

Instead, AI searches metadata first, then retrieves the best matching assets.

Metadata is the foundation of the Asset Library.

---

# Asset Model

Every asset shares the following structure.

Asset

↓

Metadata

↓

Index

↓

Search

↓

Timeline

↓

Render

---

# Core Metadata

Asset ID

Globally unique identifier.

Example

BR000001

---

Name

Human readable asset name.

Example

Office Meeting 01

---

Asset Type

Examples

B-roll

Music

Sound Effect

Motion

Subtitle Style

Hook

CTA

---

Category

High level grouping.

Examples

Business

Finance

Technology

Education

Healthcare

Lifestyle

Travel

Podcast

Gaming

---

Subcategory

Examples

Office

Laptop

Coding

Coffee

Meeting

Charts

Presentation

---

Tags

Multiple tags describing the asset.

Example

office

startup

computer

meeting

professional

team

marketing

---

Keywords

Natural language search keywords.

Example

AI startup office teamwork presentation

---

Description

Human-readable explanation.

Example

Modern office with two founders discussing startup roadmap.

---

Visual Metadata

Camera Angle

Examples

Wide

Medium

Close-up

Top View

Drone

POV

---

Camera Motion

Examples

Static

Pan

Tilt

Zoom

Tracking

Handheld

---

Lighting

Natural

Indoor

Studio

Dark

Warm

Cold

---

Color Style

Examples

Blue

Dark

Minimal

Corporate

Colorful

---

Orientation

Vertical

Horizontal

Square

---

Resolution

1080x1920

1920x1080

3840x2160

---

Frame Rate

24

30

60

FPS

---

Duration

Seconds

---

Audio Metadata

Music Genre

Corporate

Podcast

Electronic

Cinematic

Hip Hop

Lo-fi

---

Mood

Professional

Energetic

Happy

Calm

Serious

Funny

Luxury

---

Energy

1-10

---

BPM

Music only

---

Loopable

true

false

---

AI Metadata

Topic

Finance

Marketing

AI

Technology

Health

Sales

Startup

---

Intent

Teaching

Explaining

Selling

Motivating

Storytelling

Interview

Tutorial

---

Emotion

Excited

Calm

Professional

Urgent

Funny

---

Embedding ID

Reference to vector embedding.

---

Quality Score

0-100

Assigned manually or automatically.

---

Popularity Score

Calculated from user usage.

---

Usage Count

Number of productions using this asset.

---

License Metadata

License Type

Owned

Commercial

Royalty Free

Creative Commons

User Uploaded

---

Source

Internal

Purchased

Partner

User

---

Expiration Date

Optional.

---

Storage Metadata

Storage Provider

Cloudflare R2

AWS S3

Local

---

Object Key

Storage object path.

---

Thumbnail

Thumbnail path.

---

Checksum

Integrity validation.

---

Version

Asset version.

---

Design Principles

Metadata first.

AI searches metadata.

AI never searches video directly.

Every asset must be searchable.

Every asset must be reusable.

Metadata must be extensible.