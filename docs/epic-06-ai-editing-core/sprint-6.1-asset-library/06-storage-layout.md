# Asset Storage Layout

Status: Draft

Version: 1.0

---

# Principles

Files should never be stored randomly.

Storage must support millions of assets.

Directory names must remain stable.

Metadata belongs in the database.

Binary files belong in object storage.

---

Storage Architecture

Cloudflare R2

↓

Bucket

↓

Asset Type

↓

Category

↓

Subcategory

↓

Files

---

Example

assets/

broll/

business/

office/

meeting/

finance/

technology/

music/

podcast/

corporate/

electronic/

sfx/

whoosh/

click/

typing/

motions/

zoom/

fade/

subtitle-styles/

hormozi/

minimal/

podcast/

hooks/

cta/

---

File Naming

Recommended

asset_uuid.mp4

Never

final_final_v3.mp4

video123.mp4

test.mp4

---

Thumbnail Layout

thumbnails/

broll/

music/

sfx/

---

Temporary Uploads

tmp/

uploads/

processing/

---

Rendered Files

render/

production_id/

---

Generated Assets

generated/

voice/

subtitle/

music/

thumbnail/

---

Lifecycle

Upload

↓

Virus Scan

↓

Metadata Extraction

↓

Thumbnail Generation

↓

AI Tagging

↓

Database Registration

↓

Search Index

↓

Available

---

Storage Providers

Development

Local Storage

Production

Cloudflare R2

Future

AWS S3

Google Cloud Storage

Azure Blob Storage

---

Backup Strategy

Daily metadata backup.

Weekly object verification.

Monthly cold backup.

Checksum validation for every asset.