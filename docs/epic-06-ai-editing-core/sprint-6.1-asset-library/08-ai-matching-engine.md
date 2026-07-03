# AI Matching Engine

Status: Draft

Version: 1.0

---

# Purpose

The AI Matching Engine decides which assets should appear inside the final edited video.

It is the decision layer between AI understanding and timeline generation.

---

# Pipeline

Video

↓

Speech To Text

↓

Transcript

↓

Topic Detection

↓

Intent Detection

↓

Emotion Detection

↓

Editing Rules

↓

Asset Search

↓

Ranking

↓

Timeline

↓

Render

---

# Decision Inputs

Transcript

Detected Topic

Mood

Speaking Speed

Scene Context

Video Length

Style

Platform

---

# Decision Outputs

B-roll

Music

Sound Effects

Motion

Subtitle Style

Hook

CTA

---

# Rule Priority

1. Editing Rules

2. User Preferences

3. Style Engine

4. AI Matching

5. Randomization

---

# Example

Transcript

"AI giúp tiết kiệm thời gian"

↓

Topic

AI

↓

Mood

Professional

↓

Style

Business

↓

Selected Assets

Office

Laptop

Programming

Technology

Minimal Subtitle

Corporate Music

---

# Long-term Vision

The AI Matching Engine should continuously improve based on production history and user feedback.