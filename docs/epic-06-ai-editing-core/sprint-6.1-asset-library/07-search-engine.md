# Search Engine

Status: Draft

Version: 1.0

---

# Purpose

The Search Engine finds the most appropriate assets for an editing task.

Search should prioritize speed, relevance, and consistency.

---

# Search Pipeline

Transcript

↓

Intent Detection

↓

Metadata Filter

↓

Keyword Search

↓

Tag Ranking

↓

Semantic Search

↓

Popularity Score

↓

Quality Score

↓

Final Ranking

↓

Timeline Builder

---

# Search Levels

Level 1

Exact Match

Example

keyword == "office"

---

Level 2

Tag Match

office

meeting

startup

technology

---

Level 3

Metadata Match

Duration

Orientation

Mood

Resolution

Camera Angle

---

Level 4

Semantic Search

Vector similarity between transcript and asset embedding.

---

# Ranking Formula

Final Score

=

Metadata Score

+

Tag Score

+

Keyword Score

+

Embedding Score

+

Popularity

+

Quality

-

Penalty

---

# Penalties

Recently used asset

Wrong orientation

Wrong duration

Low quality

Expired license

---

# Search Performance Goals

Metadata search

< 20 ms

Hybrid search

< 100 ms

Vector search

< 300 ms

---

# Future

Hybrid Search

ElasticSearch

Vector Database

Personalized Ranking

Learning-to-Rank