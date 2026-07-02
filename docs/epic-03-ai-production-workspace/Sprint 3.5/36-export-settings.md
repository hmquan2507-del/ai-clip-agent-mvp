# Export Settings

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.5 Export Experience

---


## Purpose

Define export settings available to the user before rendering.

## Required Settings

- Format
- Resolution
- Aspect ratio
- Quality preset
- Subtitle burn-in
- Output filename

## Recommended MVP Defaults

- Format: MP4
- Resolution: 1080p
- Aspect ratio: same as approved Production
- Quality: Standard
- Subtitles: enabled if available

## Advanced Settings

Advanced settings may be added later:

- bitrate
- frame rate
- codec
- audio normalization
- platform-specific presets

## UX Rule

Export settings should use smart defaults.

Users should not need to understand video encoding to export successfully.
