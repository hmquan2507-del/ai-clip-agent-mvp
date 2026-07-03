# Asset Library Database Schema

Status: Draft

Version: 1.0

---

# Overview

The Asset Library is not a simple file storage.

It is a searchable knowledge base.

Database architecture must support:

Fast search

Semantic search

Ranking

Popularity

Usage history

Versioning

---

Entity Relationship

Asset
 │
 ├── Category
 ├── Tags
 ├── Keywords
 ├── Embedding
 ├── Usage
 ├── License
 └── Storage

---

Core Tables

Asset

Stores every asset.

Fields

id

name

type

category_id

description

duration

resolution

fps

orientation

quality_score

status

created_at

updated_at

---

Asset Category

Hierarchy of categories.

Example

Business

↓

Office

↓

Meeting

---

Asset Tag

Reusable tags.

Example

startup

office

technology

coding

AI

---

Asset Keyword

Search keywords.

---

Asset Metadata

Flexible metadata storage.

Key

Value

Example

camera_angle

close-up

---

Asset Embedding

Stores vector reference.

Fields

asset_id

embedding_provider

embedding_dimension

embedding_vector_id

---

Asset Usage

Tracks usage.

Fields

asset_id

production_id

user_id

used_at

---

Asset License

Fields

license_type

provider

expiration_date

commercial_use

---

Asset Storage

Fields

storage_provider

bucket

object_key

checksum

thumbnail

---

Indexes

Index by

Type

Category

Tags

Keywords

Mood

Topic

Duration

Orientation

Popularity

Quality Score

---

Future Expansion

Vector Database

ElasticSearch

Hybrid Search

AI Ranking

Recommendation Engine